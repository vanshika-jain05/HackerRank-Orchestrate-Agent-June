# Evaluation Report

## Pipeline Architecture
Two-stage LLM pipeline:
1. claim_extractor — extracts issue_type, object_part from conversation text
2. vision_analyser — Groq LLaMA 4 Scout vision model analyzes images vs claim
3. evidence_retriever — structured retrieval from evidence_requirements.csv
4. post_processor — validates fields, applies user history risk flags
5. Resume mode — retries only failed claims, skips successful ones

## Operational Analysis

### Model Calls
- claim_extractor: 1 call per claim (text only) = 44 calls
- vision_analyser: 1 call per claim (multimodal) = 44 calls
- Total: ~88 API calls for test set

### Token Usage (approximate)
| | Per Call | Total (44 claims) |
|---|---|---|
| Input tokens | ~2500 | ~110,000 |
| Output tokens | ~300 | ~13,200 |

### Images Processed
- Total images: ~66 (avg 1.5 per claim)
- Format: JPEG/PNG sent as base64 inline

### Cost Estimate
- Groq free tier used — $0.00
- Paid equivalent (LLaMA 4 Scout): ~$0.11 per 1M input tokens
- Estimated paid cost: < $0.02 for full test set

### Latency
- Avg per claim: ~4-6 seconds
- Total runtime: ~5-7 minutes with 1.5s sleep buffer

### Rate Limit Strategy
- 1.5s sleep between every claim call
- Exponential backoff: 3^attempt seconds on failure (1s, 3s, 9s)
- 60s wait on 429 quota errors
- Resume mode skips already-successful claims on rerun
- User history loaded once as dict — O(1) lookup
- Evidence requirements loaded once as DataFrame
- No repeated file reads during pipeline run