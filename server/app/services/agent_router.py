from __future__ import annotations

import re
from collections.abc import Callable

from pydantic import ValidationError

from app.schemas.agent_schema import AgentRoute, AgentType
from app.services.provider_errors import ProviderError, ProviderErrorCategory

_VERIFICATION_PATTERNS = (
    r"\b(?:verify|validate|fact[- ]?check)\b",
    r"\b(?:is|are|was|were|does|do|did)\b.{0,80}\b(?:supported|confirmed|verified|true according to)\b",
    r"\bdoes\b.{0,60}\b(?:support|confirm)\b",
    r"\bcheck\b.{0,60}\b(?:claim|statement|answer|supported)\b",
)
_ANALYST_PATTERNS = (
    r"\b(?:compare|comparison|trend|trends|calculate|calculation|growth rate|year[- ]over[- ]year|analy[sz]e|analysis|pattern|patterns|correlation)\b",
    r"\bhow has\b.{0,80}\bchanged\b",
    r"\bhow did\b.{0,80}\b(?:change|grow|increase|decrease|evolve)\b",
)
_SUMMARY_PATTERNS = (
    r"\b(?:summari[sz]e|summary|executive summary|overview|key takeaways|main takeaways|key points)\b",
    r"\bwhat should i know\b",
    r"\b(?:main|biggest|important) things? (?:mentioned|in|from)\b",
)
_DOCUMENT_PATTERNS = (
    r"\b(?:extract|list|identify)\b.{0,80}\b(?:dates?|requirements?|entities|sections?|metadata|facts?|fields|faq|details)\b",
    r"\b(?:important dates|functional requirements|retention target)\b",
    r"\bwhat\s+(?:was|is|are|were)\s+(?:the\s+)?(?:revenue|retention target|target|amount|date|deadline|budget|cost|requirement|owner|location|forecast|threshold)\b",
)
_RESEARCH_PATTERNS = (
    r"\bwhat does\b.{0,80}\b(?:document|report|paper|source)\b.{0,80}\bsay about\b",
    r"\b(?:explain|discuss|describe)\b.{0,80}\b(?:mentioned|discussed|in the document|in the report|based on (?:the )?(?:document|report))\b",
    r"\b(?:risks?|challenges?)\b.{0,50}\b(?:mentioned|discussed|in this report|in the document)\b",
    r"\bwhat\s+(?:are|were)\s+(?:(?:the|company's|companies')\s+)?(?:(?:major|main|biggest)\s+)?(?:risks?|challenges?)\b",
)


def _matches(question: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, question) for pattern in patterns)


def _deterministic_route(question: str) -> AgentRoute | None:
    normalized = " ".join(question.casefold().split())
    routes = (
        (
            AgentType.VERIFICATION,
            _VERIFICATION_PATTERNS,
            "The request asks to verify a claim against document evidence.",
        ),
        (
            AgentType.ANALYST,
            _ANALYST_PATTERNS,
            "The request requires comparison, calculation, or trend analysis.",
        ),
        (
            AgentType.SUMMARY,
            _SUMMARY_PATTERNS,
            "The request asks for a summary or high-level overview.",
        ),
        (
            AgentType.RESEARCH,
            _RESEARCH_PATTERNS,
            "The request asks for an explanation grounded in document content.",
        ),
        (
            AgentType.DOCUMENT,
            _DOCUMENT_PATTERNS,
            "The request asks to retrieve or extract specific document facts.",
        ),
    )
    for agent_type, patterns, reason in routes:
        if _matches(normalized, patterns):
            return AgentRoute(agent=agent_type, reason=reason)
    return None


class AgentRouter:
    """Selects a specialist agent without accessing document or retrieval data."""

    def __init__(
        self,
        strands_route: Callable[[str], AgentRoute | dict[str, object]] | None = None,
    ):
        self._strands_route = strands_route

    def route(self, question: str) -> AgentRoute:
        if not question.strip():
            raise ValueError("A question is required for automatic agent routing.")

        deterministic_route = _deterministic_route(question)
        if deterministic_route is not None:
            return deterministic_route

        if self._strands_route is None:
            from app.services.strands_router_model import route_with_strands

            route_result = route_with_strands(question)
        else:
            route_result = self._strands_route(question)

        try:
            return AgentRoute.model_validate(route_result)
        except ValidationError as exc:
            raise ProviderError(
                ProviderErrorCategory.INVALID_RESPONSE,
                provider="strands-router",
            ) from exc
