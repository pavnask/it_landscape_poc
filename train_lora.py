import json
from pathlib import Path
from typing import Dict, Any

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

SYSTEM_PROMPT = """You are a strict JSON generator.

Return exactly one JSON object with this shape:
{
  "elements": [...],
  "relations": [...]
}

Rules:
- Output JSON only
- No markdown
- No comments
- No extra keys at the top level
- Generate only NEW elements and NEW relations
- Allowed element.type: application, database, api, team, business_capability
- Allowed relation.type: owns, uses, reads_from, writes_to, exposes, supports
""".strip()

def format_example(row: Dict[str, Any]) -> Dict[str, str]:
    prompt = (
        f"<s>[INST] {SYSTEM_PROMPT}\n\n"
        f"Instruction:\n{row['instruction']}\n\n"
        f"Input:\n{row['input']} [/INST]\n"
        f"{row['output']}</s>"
    )
    return {"text": prompt}

def load_and_prepare_dataset(path: str):
    ds = load_dataset("json", data_files=path, split="train")
    return ds.map(format_example, remove_columns=ds.column_names)

def tokenize_dataset(dataset, tokenizer, max_length: int):
    def tok(batch):
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )
    return dataset.map(tok, batched=True, remove_columns=["text"])

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_file", default="train.jsonl")
    parser.add_argument("--base_model", required=True, help="HF model path or local directory, e.g. mistralai/Mistral-7B-Instruct-v0.2")
    parser.add_argument("--output_dir", default="./lora_out")
    parser.add_argument("--max_length", type=int, default=1024)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--grad_accum", type=int, default=8)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--use_4bit", action="store_true")
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quant_config = None
    if args.use_4bit:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
        )

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=quant_config,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    
    use_mps = torch.backends.mps.is_available()

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=quant_config,
        dtype=torch.float16 if use_mps else torch.float32,
    )

    if use_mps:
        model = model.to("mps")

    if args.use_4bit:
        model = prepare_model_for_kbit_training(model)

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
    )
    model = get_peft_model(model, peft_config)
    model.gradient_checkpointing_enable()
    model.config.use_cache = False
    model.print_trainable_parameters()

    train_ds = load_and_prepare_dataset(args.train_file)
    tokenized_train = tokenize_dataset(train_ds, tokenizer, args.max_length)

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        logging_steps=5,
        save_strategy="epoch",
        report_to="none",
        remove_unused_columns=False,
        gradient_checkpointing=True,
        auto_find_batch_size=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        processing_class=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()
    trainer.model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    metadata = {
        "base_model": args.base_model,
        "train_file": str(Path(args.train_file).resolve()),
        "max_length": args.max_length,
        "epochs": args.epochs,
        "learning_rate": args.lr,
    }
    Path(args.output_dir, "training_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved LoRA adapter to {args.output_dir}")

if __name__ == "__main__":
    main()
