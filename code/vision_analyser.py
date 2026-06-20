# code/vision_analyser.py

import os
import json
from dotenv import load_dotenv
from groq import Groq
import time
from time import sleep
from prompt_builder import build_system_prompt, build_user_prompt, build_messages
from evidence_retriever import EvidenceRetriever
from claim_extractor import extract_claim_info

load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyse_claim(row: dict, user_history: dict, evidence_retriever: EvidenceRetriever, images: list) -> dict:

    # Step 1: Extract what the user is actually claiming
    extracted = extract_claim_info(row["user_claim"], row["claim_object"])

    # Safeguard: If extracted is a list, extract the first dictionary element
    if isinstance(extracted, list):
        extracted = extracted[0] if len(extracted) > 0 else {}

    # CORRECTED INDENTATION: These must run regardless of whether 'extracted' was a list or a dict!
    issue_type = extracted.get("issue_type", "unknown")
    object_part = extracted.get("object_part", "unknown")
    issue_family = extracted.get("issue_family", None)

    # Step 2: Retrieve relevant evidence requirements
    evidence_text = evidence_retriever.retrieve_evidence_requirement(
        row["claim_object"]
    )

    # Step 3: Build prompts
    system_prompt = build_system_prompt()
    image_ids = [img["image_id"] for img in images]

    user_prompt = build_user_prompt(
        user_claim=row["user_claim"],
        claim_object=row["claim_object"],
        issue_type=issue_type,
        object_part=object_part,
        evidence_text=evidence_text,
        user_history=user_history or {},
        image_ids=image_ids,
    )

    # Step 4: Build multimodal message (images + text)
    contents = build_messages(user_prompt, images)

    # Step 5: Call Gemini with retry
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            *[
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{img['media_type']};base64,{img['base64']}",
                                        "detail":"auto"
                                    }
                                }
                                for img in images
                                if img.get("base64") and img.get("media_type") in ["image/jpeg", "image/png", "image/webp"]
                            ],
                            {"type": "text", "text": user_prompt}
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )

            text = response.choices[0].message.content.strip()

            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            result = json.loads(text)

            if isinstance(result, list):
                result = result[0] if len(result) > 0 else {}

            return result

        except json.JSONDecodeError:
            print(f"JSON parse failed on attempt {attempt + 1}")

        except Exception as e:
            print(f"API error on attempt {attempt + 1}: {e}")
            if "429" in str(e):
                print("Quota hit — waiting 30 seconds...")
                time.sleep(30)
            else:
                time.sleep(3 ** attempt)

    return {
        "evidence_standard_met": False,
        "evidence_standard_met_reason": "LLM call failed after retries",
        "risk_flags": "manual_review_required",
        "issue_type": "unknown",
        "object_part": "unknown",
        "claim_status": "not_enough_information",
        "claim_status_justification": "System could not process this claim",
        "supporting_image_ids": "none",
        "valid_image": False,
        "severity": "unknown"
    }


if __name__ == "__main__":
    from data_loader import DataLoader

    loader = DataLoader("../dataset")
    claims = loader.get_claims()
    row = claims[0]

    user_history = loader.get_user_history(row["user_id"])
    images = loader.load_images_as_base64(row["image_paths"])
    retriever = EvidenceRetriever("../dataset/evidence_requirements.csv")

    result = analyse_claim(row, user_history, retriever, images)
    print(result)