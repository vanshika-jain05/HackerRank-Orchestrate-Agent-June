from claim_extractor import extract_claim_info

claim = """
Customer: I am opening a claim for my windshield.
Support: What happened?
Customer: A small stone hit it while I was driving and now there is a crack spreading from that spot.
Support: Is the car otherwise okay?
Customer: Yes, this is only about the front glass.
"""

result = extract_claim_info(claim, "car")

print(result)