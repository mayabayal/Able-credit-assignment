
import os
from sentence_transformers import SentenceTransformer

def download_model():
    model_name = 'all-MiniLM-L6-v2'
    print(f"Downloading {model_name} to cache...")
    try:
        # This will download and cache the model
        model = SentenceTransformer(model_name)
        print("✅ Model downloaded successfully!")
        
        # Verify it loads from cache
        print("Verifying load...")
        model = SentenceTransformer(model_name)
        print("✅ Verified.")
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("Please check your internet connection or try again later.")

if __name__ == "__main__":
    download_model()
