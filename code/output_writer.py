# code/output_writer.py

import pandas as pd

OUTPUT_COLUMNS = [
    "user_id",
    "image_paths",
    "user_claim",
    "claim_object",
    "evidence_standard_met",
    "evidence_standard_met_reason",
    "risk_flags",
    "issue_type",
    "object_part",
    "claim_status",
    "claim_status_justification",
    "supporting_image_ids",
    "valid_image",
    "severity"
]


def build_output_row(row: dict, result: dict) -> dict:
    return {
        "user_id": row["user_id"],
        "image_paths": row["image_paths"],
        "user_claim": row["user_claim"],
        "claim_object": row["claim_object"],
        "evidence_standard_met": result.get("evidence_standard_met", False),
        "evidence_standard_met_reason": result.get("evidence_standard_met_reason", ""),
        "risk_flags": result.get("risk_flags", "none"),
        "issue_type": result.get("issue_type", "unknown"),
        "object_part": result.get("object_part", "unknown"),
        "claim_status": result.get("claim_status", "not_enough_information"),
        "claim_status_justification": result.get("claim_status_justification", ""),
        "supporting_image_ids": result.get("supporting_image_ids", "none"),
        "valid_image": result.get("valid_image", False),
        "severity": result.get("severity", "unknown")
    }


def write_output(rows: list, output_path: str):
    df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    df.to_csv(output_path, index=False)
    print(f"Output written to {output_path} — {len(df)} rows")