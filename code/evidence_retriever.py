import pandas as pd


class EvidenceRetriever:

    def __init__(self, evidence_path):
        self.evidence_df = pd.read_csv(evidence_path)

    def retrieve_evidence_requirement(
        self,
        claim_object: str
    ) -> str:

        rows = self.evidence_df[
            (self.evidence_df["claim_object"] == claim_object)
            |
            (self.evidence_df["claim_object"] == "all")
        ]

        if len(rows) == 0:
            return "No evidence requirement found."

        return "\n".join(
            rows["minimum_image_evidence"].tolist()
        )