# code/prompt_builder.py

def build_system_prompt() -> str:
    return """You are a damage claim verification AI for an insurance platform.

You will receive:
- A user's claim conversation
- One or more images of the claimed damage
- Evidence requirements for this object type
- User history context

Your job is to analyze the images and decide if they support the claim.

RULES:
1. Images are the PRIMARY source of truth
2. User history adds risk context only — it cannot override clear visual evidence
3. Output ONLY valid JSON. No explanation outside JSON.

Allowed values:
- claim_status: supported | contradicted | not_enough_information
- issue_type: dent | scratch | crack | glass_shatter | broken_part | missing_part | torn_packaging | crushed_packaging | water_damage | stain | none | unknown
- severity: none | low | medium | high | unknown
- valid_image: true | false
- evidence_standard_met: true | false

risk_flags (semicolon-separated, or "none"):
blurry_image | cropped_or_obstructed | low_light_or_glare | wrong_angle |
wrong_object | wrong_object_part | damage_not_visible | claim_mismatch |
possible_manipulation | non_original_image | text_instruction_present |
user_history_risk | manual_review_required

Car object_part: front_bumper | rear_bumper | door | hood | windshield | side_mirror | headlight | taillight | fender | quarter_panel | body | unknown
Laptop object_part: screen | keyboard | trackpad | hinge | lid | corner | port | base | body | unknown
Package object_part: box | package_corner | package_side | seal | label | contents | item | unknown

Output JSON schema:
{
  "evidence_standard_met": true or false,
  "evidence_standard_met_reason": "short reason",
  "risk_flags": "none or semicolon-separated flags",
  "issue_type": "...",
  "object_part": "...",
  "claim_status": "supported | contradicted | not_enough_information",
  "claim_status_justification": "concise image-grounded explanation mentioning image IDs",
  "supporting_image_ids": "img_1;img_2 or none",
  "valid_image": true or false,
  "severity": "none | low | medium | high | unknown"
}"""


def build_user_prompt(
    user_claim: str,
    claim_object: str,
    issue_type: str,
    object_part: str,
    evidence_text: str,
    user_history: dict,
    image_ids: list
) -> str:

    # Format user history safely
    if user_history:
        history_block = f"""Past claims: {user_history.get('past_claim_count', 'N/A')}
Accepted: {user_history.get('accept_claim', 'N/A')}
Rejected: {user_history.get('rejected_claim', 'N/A')}
Last 90 days: {user_history.get('last_90_days_claim_count', 'N/A')}
Flags: {user_history.get('history_flags', 'none')}
Summary: {user_history.get('history_summary', 'none')}"""
    else:
        history_block = "No history found for this user."

    image_ids_str = ", ".join(image_ids) if image_ids else "none"

    return f"""## Claim Conversation
{user_claim}

## Object Type
{claim_object}

## Extracted Claim Info
- Issue type claimed: {issue_type}
- Object part claimed: {object_part}

## Submitted Image IDs
{image_ids_str}

## Evidence Requirements for '{claim_object}'
{evidence_text}

## User History
{history_block}

## Your Task
Analyze the attached images carefully against the claim above.
Check if the visible damage matches what the user described.
Reference image IDs in your justification (e.g. "img_1 shows...").
Return ONLY the JSON object. No preamble, no explanation outside JSON."""


def build_messages(user_prompt: str, images: list) -> list:
    """
    Format messages for Gemini multimodal API.
    Images come first, then the text prompt.
    """
    content_parts = []

    for img in images:
        content_parts.append({
            "inline_data": {
                "mime_type": img["media_type"],
                "data": img["base64"]
            }
        })

    content_parts.append(user_prompt)

    return content_parts

# at bottom of prompt_builder.py temporarily
if __name__ == "__main__":
    print(build_system_prompt()[:200])
    print("---")
    prompt = build_user_prompt(
        user_claim="my windshield cracked",
        claim_object="car",
        issue_type="crack",
        object_part="windshield",
        evidence_text="- Must show full windshield\n- Close-up of crack required",
        user_history={"past_claim_count": 2, "rejected_claim": 0},
        image_ids=["img_1", "img_2"]
    )
    print(prompt)