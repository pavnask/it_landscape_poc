from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_path = "/Users/pavelaskolskiy/models/qwen/Qwen2.5-7B-Instruct"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16
)

if torch.backends.mps.is_available():
    model = model.to("mps")

prompt = "Почему API лучше file exchange для online интеграции?"
inputs = tokenizer(prompt, return_tensors="pt")

if torch.backends.mps.is_available():
    inputs = {k: v.to("mps") for k, v in inputs.items()}

with torch.inference_mode():
    output = model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=False
    )

print(tokenizer.decode(output[0], skip_special_tokens=True))