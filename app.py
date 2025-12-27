
import streamlit as st
import os
import tempfile
import time
from backend.ingest import PDFIngestor
from backend.rag import RAGSystem
from backend.llm import GeminiClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Financial Statement Chat",
    page_icon="ca-reports",
    layout="wide"
)

# Initialize Session State
if "rag" not in st.session_state:
    st.session_state.rag = RAGSystem()
if "ingestor" not in st.session_state:
    st.session_state.ingestor = PDFIngestor()
if "llm" not in st.session_state:
    # UPDATED: Using a widely available flash model. 
    # If you have access to specific '2.5' or '2.0' endpoints, update the model_name here.
    st.session_state.llm = GeminiClient(model_name="gemini-2.5-flash") 

if "messages" not in st.session_state:
    st.session_state.messages = []

if "evidence" not in st.session_state:
    st.session_state.evidence = []

# Sidebar for Configuration and Upload
with st.sidebar:
    st.header("Upload Financial Statement")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    
    api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key if not set in .env")
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        # Re-initialize LLM with new key
        st.session_state.llm = GeminiClient(model_name="gemini-1.5-flash")

    if uploaded_file:
        if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
            progress_text = "Operation in progress. Please wait..."
            my_bar = st.progress(0, text=progress_text)

            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Process
            try:
                # Clear old index
                st.session_state.rag.clear()
                
                # Step 1: Ingest (Parsing)
                my_bar.progress(10, text="Parsing PDF with Docling... (This handles layout & tables)")
                chunks = st.session_state.ingestor.process_pdf(tmp_path)
                
                # Step 2: Embed & Index
                TOTAL_CHUNKS = len(chunks)
                my_bar.progress(40, text=f"Extracted {TOTAL_CHUNKS} chunks. Generating Embeddings & Indexing...")
                
                # We can batch this to show more granular progress if needed, 
                # but for now we'll do it in one go or update after.
                st.session_state.rag.add_documents(chunks)
                
                my_bar.progress(100, text="Processing Complete!")
                time.sleep(1)
                my_bar.empty()
                
                st.session_state.current_file = uploaded_file.name
                st.success(f"Processed {len(chunks)} chunks from {uploaded_file.name}")
                # Cleanup
                os.unlink(tmp_path)
            except Exception as e:
                st.error(f"Error processing file: {e}")

# Main Chat Interface
st.title("Chat with Financial Statements 📊")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input
if prompt := st.chat_input("Ask a question about the financial statement..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate Answer
    if st.session_state.current_file:
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                # 1. Retrieve
                relevant_chunks = st.session_state.rag.query(prompt, k=5)
                # DEBUG: Check what we retrieved
                for i, c in enumerate(relevant_chunks):
                    print(f"Retrieval {i}: {c['text'][:100]}")
                    
                st.session_state.evidence = relevant_chunks # Store for sidebar/expander
                
                # 2. Generate
                answer = st.session_state.llm.generate_response(prompt, relevant_chunks)
                
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # 3. Show Evidence inline (optional, or kept in sidebar)
                with st.expander("View Evidence / Citations"):
                    for i, chunk in enumerate(relevant_chunks):
                        st.markdown(f"**[Source {i+1}] Page {chunk['metadata'].get('page_number', '?')}**")
                        st.text(chunk['text'][:500] + "...") # Preview
    else:
        st.error("Please upload a PDF first!")

# Evidence Sidebar (Optional: Persistent view of latest evidence)
with st.sidebar:
    st.divider()
    st.subheader("Latest Retrieval Evidence")
    if st.session_state.evidence:
        for i, chunk in enumerate(st.session_state.evidence):
            with st.expander(f"Source {i+1} (Page {chunk['metadata'].get('page_number', '?')})"):
                st.info(chunk["text"])
    else:
        st.write("No evidence retrieved yet.")
