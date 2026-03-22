import json
from pathlib import Path

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="seed_examples.jsonl")
    parser.add_argument("--synthetic", default="synthetic_examples.jsonl")
    parser.add_argument("--output", default="train.jsonl")
    args = parser.parse_args()

    out = Path(args.output)
    rows = []

    for path_str in [args.seed, args.synthetic]:
        path = Path(path_str)
        if not path.exists():
            print(f"Skipping missing file: {path}")
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))

    if not rows:
        raise SystemExit("No training rows found. Generate synthetic_examples.jsonl first.")

    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    print(f"Wrote {len(rows)} rows to {out}")

if __name__ == "__main__":
    main()
