# code/main.py

import time
import os
import pandas as pd
from data_loader import DataLoader
from evidence_retriever import EvidenceRetriever
from vision_analyser import analyse_claim
from post_processor import validate_and_fix, apply_history_risk
from output_writer import build_output_row, write_output


def run_pipeline(
    dataset_path: str = "../dataset",
    output_path: str = "../output.csv"
):
    print("Loading data...")
    loader = DataLoader(dataset_path)
    retriever = EvidenceRetriever(f"{dataset_path}/evidence_requirements.csv")

    claims = loader.get_claims()

    # RESUME LOGIC
    output_rows = []
    done_paths = set()

    if os.path.exists(output_path):
        existing = pd.read_csv(output_path)
        successful = existing[existing["claim_status"] != "not_enough_information"]
        output_rows = successful.to_dict("records")
        done_paths = set(successful["image_paths"].tolist())
        print(f"Skipping {len(successful)} successful rows, retrying the rest")

    claims = [r for r in claims if r["image_paths"] not in done_paths]
    print(f"Claims to process: {len(claims)}")

    for i, row in enumerate(claims):
        print(f"\nProcessing claim {i+1}/{len(claims)} — user: {row['user_id']}")

        try:
            user_history = loader.get_user_history(row["user_id"])
            images = loader.load_images_as_base64(row["image_paths"])

            if not images:
                result = {
                    "evidence_standard_met": False,
                    "evidence_standard_met_reason": "No images could be loaded",
                    "risk_flags": "manual_review_required",
                    "issue_type": "unknown",
                    "object_part": "unknown",
                    "claim_status": "not_enough_information",
                    "claim_status_justification": "No valid images were provided",
                    "supporting_image_ids": "none",
                    "valid_image": False,
                    "severity": "unknown"
                }
            else:
                result = analyse_claim(row, user_history, retriever, images)
                result = validate_and_fix(result)
                result = apply_history_risk(result, user_history or {})

            output_rows.append(build_output_row(row, result))
            print(f"  claim_status: {result['claim_status']} | severity: {result['severity']}")

        except Exception as e:
            print(f"  ERROR on claim {row['user_id']}: {e}")
            output_rows.append(build_output_row(row, {
                "evidence_standard_met": False,
                "evidence_standard_met_reason": "Pipeline error",
                "risk_flags": "manual_review_required",
                "issue_type": "unknown",
                "object_part": "unknown",
                "claim_status": "not_enough_information",
                "claim_status_justification": f"Processing error: {str(e)}",
                "supporting_image_ids": "none",
                "valid_image": False,
                "severity": "unknown"
            }))

        time.sleep(1.5)

    write_output(output_rows, output_path)
    print(f"\nDone. {len(output_rows)} rows written.")


if __name__ == "__main__":
    run_pipeline()