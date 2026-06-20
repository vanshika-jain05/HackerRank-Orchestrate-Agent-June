import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def extract_claim_info(user_claim, claim_object):

    prompt = f"""
You are an insurance claim extraction system.

Focus ONLY on what the CUSTOMER is claiming.

Ignore support questions.

Claim Object:
{claim_object}

Conversation:
{user_claim}

Allowed issue_type values:
dent
scratch
crack
glass_shatter
broken_part
missing_part
torn_packaging
crushed_packaging
water_damage
stain
none
unknown

Return ONLY valid JSON.

Schema:

{{
  "issue_type": "...",
  "object_part": "...",
  "issue_family": "..."
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.1
    )

    text = response.choices[0].message.content.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "").strip()

    return json.loads(text)
# If Gemini returned a list/array, safely extract the first object
    if isinstance(result, list) and len(result) > 0:
        result = result[0]

    return result