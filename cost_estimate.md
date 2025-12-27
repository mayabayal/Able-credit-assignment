# Cost Estimate Analysis

## Scenario
*   **Workload**: 1000 parallel PDF files processed/served.
*   **Operation**: Upload -> Parse (Docling) -> Embed (MiniLM) -> RAG (FAISS) -> Chat (Gemini).
*   **Assumptions**:
    *   One file per user session.
    *   Average PDF size: 50 pages.
    *   Processing time goal: < 1 minute per file.
    *   Session duration: 10 minutes.

## 1. Compute Costs (Parsing & Embedding)
This is the most resource-intensive part. `docling` with OCR and Table Extraction requires significant CPU/RAM.

*   **Resource per file**:
    *   ~2 vCPUs for decent speed parsing.
    *   ~1 GB RAM (Docling models + PDF data).
*   **Parallelism**: 1000 concurrent files.
*   **Total Requirement**: 2000 vCPUs, 1000 GB (1 TB) RAM.

**Cloud Hosting (AWS/GCP) - Spot/Preemptible Instances**:
*   Using auto-scaling node groups.
*   Instance Type: `c4.2xlarge` (8 vCPU, 15 GB RAM) can handle ~4 concurrent files.
*   Nodes needed: 1000 files / 4 = 250 instances.
*   Cost per hour (Spot `c4.2xlarge`): ~$0.10/hour.
*   Total Compute Cost: 250 instances * $0.10 = **$25.00 / hour** during peak load.

## 2. Memory (Vector Store)
*   **Model**: `all-MiniLM-L6-v2` (384 dimensions).
*   **Chunks per file**: ~50 pages * ~10 chunks/page = 500 vectors.
*   **Size per vector**: 384 dims * 4 bytes (float32) ≈ 1.5 KB.
*   **Total Size per file**: 500 * 1.5 KB ≈ 750 KB (negligible compared to parsing RAM).
*   **Conclusion**: Memory is dominated by parsing (Docling), not FAISS. The 1GB RAM per file estimate above covers this.

## 3. Storage (Ephemeral)
*   **Data**: PDFs are uploaded, processed, then deleted after session.
*   **Throughput**: 1000 files * 2 MB = 2 GB active storage.
*   **Cost**: Negligible (included in instance disk).

## 4. LLM API Costs (Gemini 1.5 Flash)
*   **Model**: Gemini 1.5 Flash (pricing is very low).
*   **Input Tokens**:
    *   Context (Chunks): ~2000 tokens per query.
    *   Prompt: ~200 tokens.
    *   Total/Query: ~2200 tokens.
*   **Output Tokens**: ~300 tokens per answer.
*   **Traffic**: Assume 10 questions per file session.
*   **Total Tokens**:
    *   Input: 2200 * 10 * 1000 = 22 Million tokens.
    *   Output: 300 * 10 * 1000 = 3 Million tokens.
*   **Pricing (Gemini 1.5 Flash)**:
    *   Input: ~$0.075 / 1M tokens.
    *   Output: ~$0.30 / 1M tokens.
*   **Total API Cost**: 
    *   (22 * 0.075) + (3 * 0.30) = $1.65 + $0.90 = **$2.55 per batch of 1000 sessions**.

## 5. Total Estimated Cost (Per Hour of Sustained 1000-user concurrency)
*   **Infrastructure (Compute/RAM)**: ~$25.00 / hour.
*   **LLM API**: (Assuming 1 batch of users per 10 mins = 6 batches/hour) -> $2.55 * 6 = $15.30 / hour.
*   **Grand Total**: **~$40.30 per hour**.

*Note: This assumes 100% utilization. Autoscaling would reduce costs significantly during low traffic.*
