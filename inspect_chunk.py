
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from reportlab.pdfgen import canvas

# Create dummy PDF
pdf_path = "dummy_inspect.pdf"
c = canvas.Canvas(pdf_path)
c.drawString(100, 750, "Hello World. This is a test document.")
c.showPage()
c.save()

converter = DocumentConverter()
result = converter.convert(pdf_path)
doc = result.document

chunker = HybridChunker()
chunk_iter = chunker.chunk(doc)

print("Inspecting first chunk:")
for chunk in chunk_iter:
    print(f"Text: {chunk.text[:50]}")
    # Check for meta
    if hasattr(chunk, 'meta'):
        print("Has 'meta'")
        # Check for doc_items in meta
        if hasattr(chunk.meta, 'doc_items'):
             print(f"Meta has 'doc_items': {len(chunk.meta.doc_items)} items")
             first_item = chunk.meta.doc_items[0]
             print(f"First item type: {type(first_item)}")
             print(f"First item dir: {dir(first_item)}")
             if hasattr(first_item, 'prov'):
                 print(f"First item prov: {first_item.prov}")
    break
