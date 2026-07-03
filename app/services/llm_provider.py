from abc import ABC, abstractmethod

from app.services.prompt_builder import ComposedPrompt


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    def generate(self, prompt: ComposedPrompt) -> str:
        """Generate a WhatsApp message from a structured prompt."""


class MockLLMProvider(LLMProvider):
    """Deterministic template-based message generator (no external API calls)."""

    def generate(self, prompt: ComposedPrompt) -> str:
        return prompt.render_template()
