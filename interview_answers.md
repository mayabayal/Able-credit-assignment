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
*   **Docling with HybridChunker**: This was the single most critical decision. Standard naive chunking (splitting by character count) failed completely ("NA" results). Switching to `HybridChunker` allowed for *semantic* segmentation, keeping sentences and table rows intact, which drastically improved retrieval relevance.
*   **Retrieval (k=5)**: We chose `k=5` to balance context. Too few fragments miss information; too many confuse the LLM.
*   **Prompt Engineering**: Enforcing "Context Only" and "Markdown Formatting" in the system prompt successfully reduced hallucinations and improved readability.

### 4. Key design choices affecting latency?
*   **Disabling Table Structure Model**: We identified that Docling's deep-learning table structure recognition was too slow for real-time use. Disabling it (`do_table_structure=False`) reduced processing time from minutes to seconds without sacrificing much text accuracy.
*   **FAISS (In-Memory)**: 100x faster than calling an external API like Pinecone for retrieval.
*   **Gemini Flash**: Chosen specifically for low-latency generation compared to GPT-4o.

### 5. Feedback mechanism to build trust?
*   **Live Evidence**: The "View Evidence / Citations" expander in the UI is the biggest trust builder. It allows the user to immediately verify if the AI made up the answer or read it from Page 48.
*   **Citations in Text**: Forcing `[Source X]` citations directly in the narrative ensures every claim is backed by a specific document part.

### 6. What if the answer lies inside a table?
*   **Ingestion**: `HybridChunker` is table-aware. Even with structure recognition disabled for speed, it preserves the textual flow of the table row-by-row, allowing the LLM (which is excellent at pattern recognition) to deduce the column values from the text sequence.

### 7. What if the answer spills over pages?
*   **Semantic Chunking**: The `HybridChunker` operates on the document object model, not just raw text. It attempts to keep logical sections together.
*   **Multi-Chunk Synthesis**: Our RAG retrieves multiple chunks. If a sentence starts on Page 4 and ends on Page 5, both chunks are likely retrieved (due to semantic similarity to the query), and the LLM combines them in the answer.

### 8. What if the answer is not present?
*   **Strict Prompting**: The system prompt explicitly commands: "If the answer is not in the context, say 'I cannot find that information in the document.'" This prevents the AI from using outside knowledge to guess (hallucinate) an answer that isn't in the specific financial statement.
