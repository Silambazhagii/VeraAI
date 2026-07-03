from typing import Any, Optional

from app.models.api_models import Decision
from app.services.llm_provider import LLMProvider, MockLLMProvider
from app.services.prompt_builder import PromptBuilder


class MessageComposer:
    """Compose personalized WhatsApp messages via structured prompts + LLM provider."""

    def __init__(
        self,
        prompt_builder: Optional[PromptBuilder] = None,
        llm_provider: Optional[LLMProvider] = None,
    ) -> None:
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._llm = llm_provider or MockLLMProvider()

    def compose(
        self,
        decision: Decision,
        category: dict[str, Any],
        merchant: dict[str, Any],
        trigger: dict[str, Any],
        customer: Optional[dict[str, Any]] = None,
    ) -> str:
        prompt = self._prompt_builder.build(
            objective=decision.objective,
            trigger_kind=trigger.get("kind", decision.objective),
            category=category,
            merchant=merchant,
            trigger=trigger,
            customer=customer,
            send_as=decision.send_as.value,
            cta=decision.cta.value,
        )
        return self._llm.generate(prompt)

    def build_template_params(
        self,
        body: str,
        merchant: dict[str, Any],
        customer: Optional[dict[str, Any]] = None,
    ) -> list[str]:
        identity = merchant.get("identity") or {}
        owner = identity.get("owner_first_name") or identity.get("name", "Merchant")
        parts = [owner]
        if len(body) > 80:
            parts.append(body[:120])
            parts.append(body[-80:])
        else:
            parts.append(body)
        if customer:
            cust_name = (customer.get("identity") or {}).get("name", "")
            if cust_name:
                parts.append(cust_name)
        return parts
