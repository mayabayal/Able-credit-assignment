
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from reportlab.pdfgen import canvas

# Create dummy PDF
pdf_path = "dummy.pdf"
c = canvas.Canvas(pdf_path)
c.drawString(100, 750, "Hello World")
c.showPage()
c.save()

print("Created dummy.pdf")

print("\n--- TEST 1: WITH WRAPPER ---")
try:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    doc_converter.convert(pdf_path)
    print("✅ Conversion Success with PdfFormatOption!")
except Exception as e:
    print(f"❌ Conversion Failed with PdfFormatOption: {e}")

print("\n--- TEST 2: WITHOUT WRAPPER (Original) ---")
try:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    
    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: pipeline_options
        }
    )
    doc_converter.convert(pdf_path)
    print("✅ Conversion Success without wrapper!")
except Exception as e:
    print(f"❌ Conversion Failed without wrapper: {e}")
