import re
from typing import Optional

from app.models.enums import Intent


_AUTO_REPLY_PATTERNS = [
    r"thank you for contacting",
    r"auto[\s-]?reply",
    r"\baway\b",
    r"office hours",
    r"business account",
    r"welcome message",
    r"our team will respond",
    r"automated assistant",
    r"we will get back to you",
    r"bahut[\s-]?bahut shukriya",
    r"hamari team tak pahuncha",
]


class AutoReplyDetector:
    """Detect WhatsApp Business auto-replies and canned responses."""

    def __init__(self) -> None:
        self._compiled = [re.compile(p, re.IGNORECASE) for p in _AUTO_REPLY_PATTERNS]

    def is_auto_reply(self, message: str, history: Optional[list[str]] = None) -> bool:
        text = message.strip().lower()
        if not text:
            return False

        for pattern in self._compiled:
            if pattern.search(text):
                return True

        if history:
            same_count = sum(1 for h in history if h.strip().lower() == text)
            if same_count >= 1:
                return True

        return False

    def classify_as_intent(self, message: str, history: Optional[list[str]] = None) -> Intent:
        if self.is_auto_reply(message, history):
            return Intent.AUTO_REPLY
        return Intent.UNKNOWN


auto_reply_detector = AutoReplyDetector()
