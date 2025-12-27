
import os
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # Fallback for demo purposes if environment variable is not set
            # Ideally this should be handled gracefully in the UI
            print("Warning: GEMINI_API_KEY not found in environment.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_response(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Generates an answer using Gemini based on the provided context.
        """
        
        context_str = ""
        for i, chunk in enumerate(context_chunks):
            # We add a Source ID [Source X] to the context so the LLM can reference it.
            context_str += f"\n[Source {i+1}] (Page {chunk['metadata'].get('page_number', '?')}):\n{chunk['text']}\n"

        prompt = f"""
You are a smart financial analyst assistant. 

### INSTRUCTIONS:
1.  **Greeting**: If the user greets you (e.g., "hi"), greet back politely and offer help with the financial statement.
2.  **Context Only**: Answer the user's question using **ONLY** the provided context pieces below. Do not use outside knowledge.
3.  **No Info**: If the answer is not in the context, say "I cannot find that information in the document."
4.  **Formatting**: Format your answer clearly using **Markdown**:
    *   Use **bold** for key metrics or numbers.
    *   Use bullet points or numbered lists for steps.
    *   Use tables if comparing multiple data points.
5.  **Citations**: You **MUST** cite your sources for every fact using `[Source X]`.

### EXAMPLE:
"The **Net Revenue** increased by 15% to $5B [Source 1], while **Operating Costs** decreased by 5% [Source 2]."

Question: {question}

Context:
{context_str}

Answer:
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
