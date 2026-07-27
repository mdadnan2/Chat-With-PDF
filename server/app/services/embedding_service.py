from google import genai

from app.config import settings


class EmbeddingService:

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)

    def generate_embedding(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )

        return response.embeddings[0].values

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
        )

        return [e.values for e in response.embeddings]
