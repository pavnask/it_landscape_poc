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

## 6) Richer held-out evaluation

Use the richer test set and stricter semantic validator:

```bash
python semantic_validator.py train.jsonl
python heldout_eval.py --model mistral --tests heldout_eval_set.json --output heldout_eval_results.json
```

Files:
- `heldout_eval_set.json` — 12 held-out tests with expected output shape
- `semantic_validator.py` — structural + semantic validation
- `heldout_eval.py` — runs Ollama against the held-out set

## 7) Prepare train.jsonl

```bash
python prepare_train.py --seed seed_examples.jsonl --synthetic synthetic_examples.jsonl --output train.jsonl
```

## 8) LoRA training

Install dependencies in a fresh venv if possible:

```bash
pip install -r requirements-lora.txt
```

Train on a Hugging Face compatible Mistral-family model:

```bash
python train_lora.py   --train_file train.jsonl   --base_model mistralai/Mistral-7B-Instruct-v0.2   --output_dir lora_out   --use_4bit
```

Notes:
- `train_lora.py` trains a PEFT/LoRA adapter, not a merged full model.
- For CPU-only environments, remove `--use_4bit`, but training may be too slow.
- This script assumes a decoder-only causal LM with Mistral-style module names.
- I did not execute the training here, so treat it as a ready-to-run starting script and adjust batch size or target modules if your base model differs.

## 9) Compare baseline vs tuned model

Recommended comparison:
1. Run `heldout_eval.py` on the base model.
2. Load the LoRA adapter in your inference path.
3. Run the same held-out set again.
4. Compare:
   - parse rate
   - semantic-valid rate
   - task-match rate
   - relation-choice consistency
