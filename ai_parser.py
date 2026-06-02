import json
import os
import time

from env_utils import load_local_env


MODEL_NAMES = [
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]


def parse_order(message, image_path=None):
    load_local_env()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Set GEMINI_API_KEY before parsing WhatsApp orders. "
            "Either run `$env:GEMINI_API_KEY=\"your_key\"` in PowerShell "
            "or add GEMINI_API_KEY=your_key to a local .env file."
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError(
            "The google-genai package is not installed in this Python interpreter. "
            "Run this project with `.\\venv\\Scripts\\python.exe workflow.py`, "
            "or install dependencies with `python -m pip install -r requirements.txt`."
        ) from exc

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an order extraction system for WhatsApp messages.

Extract customer name if present.

Extract all products and quantities.
If an image is provided, analyze the image (e.g., handwritten lists, product photos, invoices) and extract the products and quantities from it as well. Combine findings from both the text and the image.

If the message is casual conversation, a greeting, a question with no product
order, or does not clearly ask for products/quantities (both in text and image), set "is_order" to false
and return an empty items list.

Return ONLY valid JSON.

Format:

{{
    "is_order": false,
    "customer_name": null,
    "items": [
        {{
            "product": "",
            "qty": 0
        }}
    ]
}}

Message:

{message}
"""

    contents = [prompt]
    uploaded_file = None
    
    if image_path:
        print(f"Uploading image {image_path} to Gemini...")
        uploaded_file = client.files.upload(file=image_path)
        contents.append(uploaded_file)

    last_error = None

    try:
        for model_name in MODEL_NAMES:
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )

                    response_text = (response.text or "").strip()
                    return parse_json_response(response_text)

                except Exception as exc:
                    last_error = exc

                    if not is_temporary_ai_error(exc):
                        raise

                    wait_seconds = attempt + 1
                    print(
                        f"AI model busy ({model_name}). "
                        f"Retrying in {wait_seconds}s..."
                    )
                    time.sleep(wait_seconds)

        raise RuntimeError(
            "AI parser is temporarily unavailable after retries. "
            "Please try again in a minute."
        ) from last_error
    finally:
        if uploaded_file:
            try:
                print(f"Deleting file {uploaded_file.name} from Gemini servers...")
                client.files.delete(name=uploaded_file.name)
            except Exception as e:
                print(f"Failed to delete file from Gemini: {e}")


def is_temporary_ai_error(exc):
    error_text = str(exc).lower()

    return (
        "503" in error_text
        or "unavailable" in error_text
        or "temporarily" in error_text
        or "high demand" in error_text
        or "rate limit" in error_text
        or "resource_exhausted" in error_text
    )


def parse_json_response(response_text):
    response_text = response_text.strip()

    if response_text.startswith("```"):
        response_text = (
            response_text
                .removeprefix("```json")
                .removeprefix("```")
                .strip()
        )
        response_text = response_text.removesuffix("```").strip()

    if not response_text:
        raise ValueError("AI parser returned an empty response.")

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI parser returned invalid JSON: {response_text}") from exc


if __name__ == "__main__":
    message = """
My name is Rahul Sharma

Need 2 Cabinet with Doors
and 3 Acoustic Bloc Screens
"""

    result = parse_order(message)

    print(result)
