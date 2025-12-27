
import os
from typing import List, Dict, Any, Generator
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.chunking import HybridChunker

class PDFIngestor:
    def __init__(self):
        # Configure Docling options
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False 
        pipeline_options.do_table_structure = False 

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )
        self.chunker = HybridChunker(tokenizer="sentence-transformers/all-MiniLM-L6-v2")

    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Parses a PDF file and returns a list of chunks with metadata.
        Uses HybridChunker for high-quality semantic extraction.
        """
        print(f"Processing PDF: {pdf_path}")
        result = self.converter.convert(pdf_path)
        doc = result.document
        
        chunks = []
        
        # Use HybridChunker to get semantic chunks (text + tables included)
        chunk_iter = self.chunker.chunk(doc)
        
        for i, chunk_obj in enumerate(chunk_iter):
            text_content = chunk_obj.text.strip()
            if not text_content:
                continue
            
            # Extract Page Number from provenance
            page_no = -1
            if hasattr(chunk_obj, 'meta') and hasattr(chunk_obj.meta, 'doc_items'):
                for item in chunk_obj.meta.doc_items:
                    if hasattr(item, 'prov') and item.prov:
                        page_no = item.prov[0].page_no
                        break

            if len(chunks) < 10: # Print first 10
                print(f"DEBUG INGEST CHUNK {i}: {text_content[:50]}...")
            
            chunk = {
                "text": text_content,
                "metadata": {
                    "source": os.path.basename(pdf_path),
                    "page_number": page_no,
                    "chunk_id": i
                }
            }
            chunks.append(chunk)

        print(f"Extracted {len(chunks)} chunks from {pdf_path}")
        # Verify if empty
        if not chunks:
            print("WARNING: No chunks extracted!")
        else:
            print(f"Sample Chunk 0: {chunks[0]['text'][:100]}...")
            
        return chunks
