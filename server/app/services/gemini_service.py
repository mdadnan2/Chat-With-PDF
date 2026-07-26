from google import genai

from app.config import settings


class GeminiService:

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)

    def generate_answer(self, prompt: str) -> str:
        print(f"Using model: {settings.gemini_chat_model}")
        
        response = self.client.models.generate_content(
            model=settings.gemini_chat_model,
            contents=prompt,
        )

        return response.text
