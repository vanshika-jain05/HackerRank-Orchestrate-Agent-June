from evidence_retriever import EvidenceRetriever

retriever = EvidenceRetriever(
    "../dataset/evidence_requirements.csv"
)

print(
    retriever.retrieve_evidence_requirement(
        "car"
    )
)