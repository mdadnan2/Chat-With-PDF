from app.services.openai_compatible_provider import OpenAICompatibleGenerationProvider


class OpenRouterGenerationProvider(OpenAICompatibleGenerationProvider):
    provider_name = "openrouter"
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
