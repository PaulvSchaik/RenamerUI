import fitz  # PyMuPDF
from google import genai
from dotenv import load_dotenv
import json
import os

load_dotenv()

client = None


def initialize_client(api_key: str):
    """Initialize (or re-initialize) the Gemini client with the given API key."""
    global client
    client = genai.Client(api_key=api_key) if api_key else None


# Auto-initialize from .env if a key is available (useful during development)
initialize_client(os.getenv("GOOGLE_API_KEY", ""))


def extract_text_from_pdf(file_path, max_pages=3):
    """Extracts text from the first few pages of a PDF."""
    text = ""
    try:
        doc = fitz.open(file_path)
        for i in range(min(len(doc), max_pages)):
            text += doc[i].get_text()
        doc.close()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text


def get_pdf_metadata(text):
    """Uses Gemini to extract year-month, party, and summary from text."""
    if not text.strip() or client is None:
        return None

    prompt = f"""
    Analyze the following text from a PDF document and extract metadata for renaming the file.
    The filename format must be: YYYY-MM - [Involved Party] - [Short Summary].pdf

    Extract:
    1. year_month: The date of the document in YYYY-MM format. If only a year is found, use YYYY-01. If no date, use the current year-month.
    2. party: The main company, sender, or involved party (e.g., 'Google', 'Belastingdienst', 'Werkgever'). Max 3 words.
    3. summary: A very brief description of the content (e.g., 'Factuur', 'Loonstrook', 'Contract'). Max 5 words.

    Return the result strictly as a JSON object with keys: "year_month", "party", "summary".
    Do not include any other text or markdown formatting in your response.

    Text:
    {text[:4000]}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        clean_response = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_response)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None
