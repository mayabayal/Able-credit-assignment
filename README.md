# Financial Statement Chat with Citations

A RAG-based chat system for financial statements that provides precise citations and evidence for every answer.

## Architecture

The system is built using a modular RAG (Retrieval-Augmented Generation) pipeline:

1.  **Ingestion Layer (`backend/ingest.py`)**:
    *   **Library**: `docling` (IBM) is used for PDF parsing.
    *   **Reasoning**: Unlike basic text extractors, `docling` understands document layout (reading order, tables, headers), which is crucial for financial reports.
    *   **Process**: The PDF is parsed into a structured format. We iterate through text and tables, tagging each chunk with its **Page Number** and Source Filename.

2.  **Storage & Retrieval Layer (`backend/rag.py`)**:
    *   **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`. This model is lightweight, fast, and runs locally.
    *   **Vector Store**: `FAISS`. We use an in-memory index for the session.
    *   **Reasoning**: For a single-file chat session, a full vector DB (Pinecone/Milvus) is overkill. FAISS provides millisecond retrieval latency with zero infrastructure cost.

3.  **Generation Layer (`backend/llm.py`)**:
    *   **Model**: **Google Gemini 1.5 Flash**.
    *   **Reasoning**: Extremely fast, low cost, and large context window.
    *   **Citation Logic**: The prompt strictly instructs the model to use `[Source X]` references, which the UI maps back to the specific text chunk and page number.

4.  **UI Layer (`app.py`)**:
    *   **Framework**: `Streamlit`.
    *   **Features**:
        *   Drag-and-drop PDF upload.
        *   Chat interface.
        *   **Dedicated Evidence Panel**: Verifies the AI's claims by showing the raw retrieved text next to the answer.

## Setup & Run

### Prerequisites
*   Python 3.10+
*   `uv` (Package manager) or `pip`
*   Google Gemini API Key

### Installation

1.  **Initialize Environment**:
    ```bash
    uv sync
    # OR if using pip
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    *   Rename `.env.example` to `.env` and add your `GEMINI_API_KEY`.
    *   Or enter the key directly in the UI sidebar.

### Running the App
```bash
uv run streamlit run app.py
```

## Cost Estimate (Summary)
For a production system serving 1000 concurrent files:
*   **Hosting**: ~$40/hour total.
*   **Breakdown**:
    *   Compute (Parsing): $25/hr (Spot instances).
    *   LLM API: ~$15/hr (Gemini Flash).
    *   Detailed analysis in [cost_estimate.md](cost_estimate.md).
