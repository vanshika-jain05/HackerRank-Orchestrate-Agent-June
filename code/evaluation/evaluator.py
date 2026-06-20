# evaluation/evaluator.py

import pandas as pd

FIELDS_TO_CHECK = [
    "claim_status",
    "issue_type", 
    "object_part",
    "severity",
    "evidence_standard_met",
    "valid_image"
]

def evaluate(sample_path: str, predicted_path: str):
    sample = pd.read_csv(sample_path)
    predicted = pd.read_csv(predicted_path)

    # Match on user_id
    merged = sample.merge(predicted, on="user_id", suffixes=("_actual", "_pred"))

    print(f"Total rows evaluated: {len(merged)}\n")

    total_score = 0

    for field in FIELDS_TO_CHECK:
        actual_col = f"{field}_actual"
        pred_col = f"{field}_pred"

        if actual_col not in merged.columns or pred_col not in merged.columns:
            print(f"{field}: columns missing, skipping")
            continue

        matches = (
            merged[actual_col].astype(str).str.lower() ==
            merged[pred_col].astype(str).str.lower()
        ).sum()

        pct = 100 * matches / len(merged)
        total_score += pct
        print(f"{field:30s}: {matches}/{len(merged)} ({pct:.1f}%)")

    print(f"\nOverall average accuracy: {total_score / len(FIELDS_TO_CHECK):.1f}%")


if __name__ == "__main__":
    evaluate(
        sample_path="../../dataset/sample_claims.csv",
        predicted_path="../../dataset/sample_output.csv"  # your predictions on sample
    )