# Interview Questions & Answers

### 1. How will this work when we get multiple requests, each of large PDF files?
*   **State Management**: Since we use **Streamlit**, each user session is independent. The `session_state` stores the FAISS index *in memory* for that specific user.
*   **Scaling**: The bottleneck is memory (RAM). Each active user loads a PDF and an index into RAM.
    *   **Solution**: Deploy behind a Load Balancer with "sticky sessions". Scale horizontally by adding more worker nodes (Streamlit containers) as traffic increases.
    *   **Async Processing**: For very large files, move the ingestion (`docling` processing) to a background worker queue (e.g., Celery/Redis) so the UI doesn't freeze.

### 2. What are the main bottlenecks of the system?
*   **CPU (Parsing)**: `docling` uses deep learning models for layout analysis and OCR. This is the slowest step (Seconds to Minutes depending on PDF text-density).
*   **Ram**: Storing uncompressed text chunks and FAISS indices for thousands of concurrent users will consume significant memory.
*   **Latency**: If using a large LLM, generation time can be a bottleneck, though Gemini Flash is very fast.

### 3. Key choices affecting accuracy?
*   **Parsing Quality (Docling)**: Choosing `docling` over `pypdf` is the biggest accuracy booster. It correctly identifies tables and multi-column layouts, preventing "gibberish" chunks.
*   **Chunking Strategy**: We currently chunk by "paragraph/element". If chunks are too small, context is lost. If too large, retrieval is imprecise.
*   **Retrieval (k=5)**: Changing `k` affects how much context the LLM sees. Too few = missed info; Too many = distraction.

### 4. Key design choices affecting latency?
*   **FAISS (In-Memory)**: 100x faster than calling an external API like Pinecone for retrieval.
*   **Embedding Model**: using a "Mini" model (all-MiniLM-L6) is much faster than `bert-base` or OpenAI embeddings, with minimal accuracy loss for this use case.
*   **Gemini Flash**: Chosen specifically for low-latency generation compared to GPT-4o.

### 5. Feedback mechanism to build trust?
*   **Citations**: The system *must* link answers to specific page numbers.
*   **Evidence Snippets**: Showing the *exact text* used for the answer (quoted in the UI) allows users to verify "hallucinations" instantly.
*   **Confidence Score**: We could display the "distance score" from FAISS to indicate how relevant the found information was.

### 6. What if the answer lies inside a table?
*   **Ingestion**: `docling` preserves table structure. We convert tables to CSV/Markdown format in the chunk.
*   **LLM Handling**: LLMs are good at reading CSV/Markdown tables. The RAG retrieves the table representation, and the LLM interprets the row/column to answer.

### 7. What if the answer spills over pages?
*   **Windowing**: We capture page numbers. A sophisticated chunking strategy (sliding window) can include overlaps between pages.
*   **Metadata**: Our chunks are page-aware. If we retrieve chunks from Page 5 and Page 6, the LLM can synthesize information across them.
