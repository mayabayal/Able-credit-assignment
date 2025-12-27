
try:
    from docling.chunking import HybridChunker
    print("✅ HybridChunker found!")
except ImportError:
    print("❌ HybridChunker NOT found.")
    import docling
    print(f"Docling version: {docling.__version__}")
    print(dir(docling))
