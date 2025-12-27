
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

try:
    print("Attempting instantiation with PdfFormatOption...")
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    print("Success with PdfFormatOption!")
except Exception as e:
    print(f"Failed with PdfFormatOption: {e}")

try:
    print("\nAttempting instantiation WITHOUT wrapper (Original Code)...")
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: pipeline_options
        }
    )
    print("Success without wrapper!")
except Exception as e:
    print(f"Failed without wrapper: {e}")
