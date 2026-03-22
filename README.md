# IT Landscape LoRA POC Starter Pack

This folder gives you a minimal starting point for a proof of concept:

- `schema.json` — small target schema
- `seed_examples.jsonl` — 20 seed instruction-tuning examples
- `generate_synthetic_data.py` — expands into synthetic JSONL examples
- `validate_dataset.py` — validates outputs in a JSONL dataset
- `baseline_eval.py` — runs a quick baseline against a local Ollama model

## 1) Validate the seed dataset

```bash
python validate_dataset.py seed_examples.jsonl
```

## 2) Generate synthetic examples

```bash
python generate_synthetic_data.py --count 100 --output synthetic_examples.jsonl
python validate_dataset.py synthetic_examples.jsonl
```

## 3) Combine datasets

Linux/macOS:
```bash
cat seed_examples.jsonl synthetic_examples.jsonl > train.jsonl
```

Windows PowerShell:
```powershell
Get-Content seed_examples.jsonl, synthetic_examples.jsonl | Set-Content train.jsonl
```

## 4) Baseline your local model in Ollama

```bash
python baseline_eval.py --model mistral --output baseline_eval_results.json
```

The baseline script checks one thing first: can the base model return valid JSON in your shape for held-out prompts?

## 5) Next step for LoRA

Ollama is fine for inference, but LoRA training is usually easier with Hugging Face + PEFT.
A common workflow is:

1. pick a compatible base model in Hugging Face format
2. convert `train.jsonl` to your chosen fine-tuning format
3. train a LoRA adapter
4. compare baseline vs tuned model on the same held-out prompts
5. score:
   - JSON parse success
   - schema validity
   - allowed relation types
   - sensible element naming
   - lower hallucination rate

## Suggested POC success criteria

A good first success bar is:

- >90% valid JSON on held-out prompts
- >80% schema-valid outputs
- better consistency after LoRA than the base model
- outputs that are useful enough for human review, not fully autonomous changes

## Suggested next expansion

After this starter pack works, expand in this order:

1. add more examples per pattern
2. add more industries and naming conventions
3. add negative examples for invalid relations
4. add context-rich prompts with 4–8 existing elements
5. add a business-description-to-JSON task as a second benchmark
