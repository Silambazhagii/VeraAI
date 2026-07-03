import threading
from typing import Optional

from app.core.logger import get_logger
from app.models.conversation import ConversationState, ConversationTurn
from app.models.enums import ConversationStatus, Intent, SendAs

logger = get_logger(__name__)


class ConversationManager:
    """In-memory conversation state manager."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._conversations: dict[str, ConversationState] = {}
        self._active_by_merchant_trigger: dict[str, str] = {}

    def _dedup_key(self, merchant_id: str, trigger_id: str) -> str:
        return f"{merchant_id}:{trigger_id}"

    def has_active_conversation(self, merchant_id: str, trigger_id: str) -> bool:
        with self._lock:
            key = self._dedup_key(merchant_id, trigger_id)
            conv_id = self._active_by_merchant_trigger.get(key)
            if not conv_id:
                return False
            conv = self._conversations.get(conv_id)
            return conv is not None and conv.status == ConversationStatus.ACTIVE

    def create(
        self,
        conversation_id: str,
        merchant_id: str,
        trigger_id: str,
        send_as: SendAs,
        trigger_kind: str,
        suppression_key: str,
        customer_id: Optional[str] = None,
        pending_action: Optional[str] = None,
    ) -> ConversationState:
        with self._lock:
            state = ConversationState(
                conversation_id=conversation_id,
                merchant_id=merchant_id,
                customer_id=customer_id,
                trigger_id=trigger_id,
                send_as=send_as,
                trigger_kind=trigger_kind,
                suppression_key=suppression_key,
                pending_action=pending_action,
            )
            self._conversations[conversation_id] = state
            self._active_by_merchant_trigger[self._dedup_key(merchant_id, trigger_id)] = conversation_id
            logger.info("Created conversation %s for merchant %s", conversation_id, merchant_id)
            return state

    def get(self, conversation_id: str) -> Optional[ConversationState]:
        with self._lock:
            return self._conversations.get(conversation_id)

    def add_turn(
        self,
        conversation_id: str,
        role: str,
        message: str,
        turn_number: int,
        received_at: str = "",
    ) -> Optional[ConversationState]:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if not conv:
                return None
            conv.history.append(
                ConversationTurn(
                    turn_number=turn_number,
                    role=role,
                    message=message,
                    received_at=received_at,
                )
            )
            return conv

    def record_bot_message(self, conversation_id: str, body: str) -> None:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                conv.bodies_sent.append(body)

    def body_already_sent(self, conversation_id: str, body: str) -> bool:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            return body in conv.bodies_sent if conv else False

    def set_intent(self, conversation_id: str, intent: Intent) -> None:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                conv.last_intent = intent

    def set_pending_action(self, conversation_id: str, action: Optional[str]) -> None:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                conv.pending_action = action

    def increment_auto_reply(self, conversation_id: str) -> int:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                conv.auto_reply_count += 1
                return conv.auto_reply_count
            return 0

    def end(self, conversation_id: str) -> None:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                conv.status = ConversationStatus.ENDED
                key = self._dedup_key(conv.merchant_id, conv.trigger_id)
                if self._active_by_merchant_trigger.get(key) == conversation_id:
                    del self._active_by_merchant_trigger[key]

    def set_waiting(self, conversation_id: str) -> None:
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                conv.status = ConversationStatus.WAITING

    def clear(self) -> None:
        with self._lock:
            self._conversations.clear()
            self._active_by_merchant_trigger.clear()


_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    global _manager
    if _manager is None:
        _manager = ConversationManager()
    return _manager
