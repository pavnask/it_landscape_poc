#!/usr/bin/env python3
"""
LoRA training script for chat/messages format JSONL.

Expected dataset format (one JSON object per line):
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}

Example:
python train_lora_messages.py \
  --train_file reasoning_dataset_v1.jsonl \
  --base_model Qwen/Qwen2.5-1.5B-Instruct \
  --output_dir lora_qwen_reasoning_v1 \
  --epochs 1 \
  --lr 2e-4
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_file", required=True, help="Path to messages-format JSONL")
    parser.add_argument("--base_model", required=True, help="HF model id")
    parser.add_argument("--output_dir", required=True, help="Where to save LoRA adapter")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max_length", type=int, default=1024)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--grad_accum", type=int, default=8)
    parser.add_argument("--logging_steps", type=int, default=5)
    parser.add_argument("--save_strategy", default="epoch", choices=["no", "steps", "epoch"])
    parser.add_argument("--lora_r", type=int, default=16)
    parser.add_argument("--lora_alpha", type=int, default=32)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    return parser.parse_args()


def load_and_prepare_dataset(path: str, tokenizer, max_length: int):
    ds = load_dataset("json", data_files=path, split="train")

    def validate_messages(example: Dict[str, Any]) -> Dict[str, Any]:
        if "messages" not in example or not isinstance(example["messages"], list) or len(example["messages"]) == 0:
            raise ValueError("Each row must contain non-empty 'messages' list")
        for msg in example["messages"]:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValueError("Each message must be an object with 'role' and 'content'")
        return example

    ds = ds.map(validate_messages)

    def format_and_tokenize(example: Dict[str, Any]) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = example["messages"]

        # Use tokenizer chat template when available
        if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
        else:
            # Fallback plain formatting
            chunks = []
            for msg in messages:
                chunks.append(f"{msg['role'].upper()}: {msg['content']}")
            text = "\n\n".join(chunks)

        encoded = tokenizer(
            text,
            truncation=True,
            max_length=max_length,
            padding=False,
        )

        encoded["labels"] = encoded["input_ids"].copy()
        return encoded

    ds = ds.map(
        format_and_tokenize,
        remove_columns=ds.column_names,
    )
    return ds


def pick_target_modules(model_name: str) -> List[str]:
    name = model_name.lower()
    if "qwen" in name or "mistral" in name or "llama" in name:
        return ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    return ["q_proj", "v_proj"]


def main():
    args = parse_args()

    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Loading base model...")
    dtype = torch.float16 if torch.backends.mps.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(args.base_model, dtype=dtype)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=pick_target_modules(args.base_model),
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    train_ds = load_and_prepare_dataset(args.train_file, tokenizer, args.max_length)

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        logging_steps=args.logging_steps,
        save_steps=100,
        save_total_limit=1,
        do_eval=False,
        report_to=[],
        fp16=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        data_collator=data_collator,
    )

    trainer.train()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"Saved LoRA adapter to {args.output_dir}")


if __name__ == "__main__":
    main()
