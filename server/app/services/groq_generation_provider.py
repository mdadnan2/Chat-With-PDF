from app.services.openai_compatible_provider import OpenAICompatibleGenerationProvider


class GroqGenerationProvider(OpenAICompatibleGenerationProvider):
    provider_name = "groq"
    endpoint = "https://api.groq.com/openai/v1/chat/completions"
