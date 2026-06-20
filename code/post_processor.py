# code/post_processor.py

ALLOWED_CLAIM_STATUS = {"supported", "contradicted", "not_enough_information"}
ALLOWED_ISSUE_TYPES = {
    "dent", "scratch", "crack", "glass_shatter", "broken_part",
    "missing_part", "torn_packaging", "crushed_packaging",
    "water_damage", "stain", "none", "unknown"
}
ALLOWED_SEVERITY = {"none", "low", "medium", "high", "unknown"}
ALLOWED_RISK_FLAGS = {
    "none", "blurry_image", "cropped_or_obstructed", "low_light_or_glare",
    "wrong_angle", "wrong_object", "wrong_object_part", "damage_not_visible",
    "claim_mismatch", "possible_manipulation", "non_original_image",
    "text_instruction_present", "user_history_risk", "manual_review_required"
}


def validate_and_fix(output: dict) -> dict:
    if output.get("claim_status") not in ALLOWED_CLAIM_STATUS:
        output["claim_status"] = "not_enough_information"

    if output.get("issue_type") not in ALLOWED_ISSUE_TYPES:
        output["issue_type"] = "unknown"

    if output.get("severity") not in ALLOWED_SEVERITY:
        output["severity"] = "unknown"

    # Validate each risk flag
    flags = output.get("risk_flags", "none")
    if flags and flags != "none":
        flag_list = [f.strip() for f in flags.split(";")]
        valid_flags = [f for f in flag_list if f in ALLOWED_RISK_FLAGS]
        output["risk_flags"] = ";".join(valid_flags) if valid_flags else "none"

    # Ensure booleans are actual booleans
    for bool_field in ["evidence_standard_met", "valid_image"]:
        val = output.get(bool_field)
        if isinstance(val, str):
            output[bool_field] = val.lower() == "true"

    return output


def apply_history_risk(output: dict, user_history: dict) -> dict:
    if not user_history:
        return output

    flags = output.get("risk_flags", "none")
    flag_list = [] if flags == "none" else flags.split(";")

    rejected = user_history.get("rejected_claim", 0)
    last_90 = user_history.get("last_90_days_claim_count", 0)
    history_flags = user_history.get("history_flags", "")

    # Add risk flags if history looks suspicious
    if rejected >= 2 or last_90 >= 3 or (history_flags and history_flags != "none"):
        if "user_history_risk" not in flag_list:
            flag_list.append("user_history_risk")
        if "manual_review_required" not in flag_list:
            flag_list.append("manual_review_required")

    output["risk_flags"] = ";".join(flag_list) if flag_list else "none"
    return output