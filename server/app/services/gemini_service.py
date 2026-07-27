from google import genai
from app.config import settings
import re
from app.schemas.retrieval_schema import RetrievedChunk


class GeminiService:

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)

    def generate_answer(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=settings.gemini_chat_model,
            contents=prompt,
        )

        return response.text

    def rerank_chunks(
        self,
        question: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:

        if not chunks:
            return []

        chunk_text = ""

        for index, chunk in enumerate(chunks, start=1):
            chunk_text += f"""
Chunk {index}

Heading:
{chunk.heading}

Content:
{chunk.content}

----------------------------------------
"""

        prompt = f"""
You are an expert retrieval reranker.

Your ONLY task is to rank the chunks.

Do NOT answer the question.

Question:
{question}

Chunks:

{chunk_text}

Return ONLY the 5 most relevant chunk numbers.

Example:
2,1,3,4,5
"""

        response = self.client.models.generate_content(
            model=settings.gemini_chat_model,
            contents=prompt,
        )

        ranking_text = response.text.strip()

        numbers = re.findall(r"\d+", ranking_text)[:5]

        if not numbers:
            return chunks

        ranked_indexes = [int(n) - 1 for n in numbers]

        reranked = []

        for index in ranked_indexes:
            if 0 <= index < len(chunks):
                reranked.append(chunks[index])

        for i, chunk in enumerate(chunks):
            if i not in ranked_indexes:
                reranked.append(chunk)

        return reranked
