import re
from typing import Optional

from app.models.enums import Intent
from app.services.auto_reply_detector import auto_reply_detector


class IntentClassifier:
    """Rule-based intent classification for merchant/customer replies."""

    _STOP = re.compile(
        r"\b(stop|unsubscribe|not interested|spam|leave me alone|band karo|mat bhejo)\b",
        re.IGNORECASE,
    )
    _YES = re.compile(
        r"\b(yes|yeah|yep|ok|okay|sure|go ahead|let'?s do it|confirm|proceed|haan|ha|theek)\b",
        re.IGNORECASE,
    )
    _NO = re.compile(r"\b(no|nope|nah|not now|cancel|mat)\b", re.IGNORECASE)
    _CALL = re.compile(r"\b(call me|phone|callback|ring me|call karo)\b", re.IGNORECASE)
    _PRICE = re.compile(r"\b(price|cost|kitna|rate|charges|fees|₹|rs\.?)\b", re.IGNORECASE)
    _DETAILS = re.compile(
        r"\b(details|more info|tell me more|explain|batao|share|abstract|draft)\b",
        re.IGNORECASE,
    )
    _LATER = re.compile(r"\b(later|busy|abhi nahi|not now|kal|baad mein|some other time)\b", re.IGNORECASE)
    _QUESTION = re.compile(r"(\?|kya |kaise |kab |why |what |how )", re.IGNORECASE)

    def classify(self, message: str, history: Optional[list[str]] = None) -> Intent:
        text = message.strip()
        if not text:
            return Intent.UNKNOWN

        merchant_history = history or []
        if auto_reply_detector.is_auto_reply(text, merchant_history):
            return Intent.AUTO_REPLY

        if self._STOP.search(text):
            return Intent.STOP
        if self._CALL.search(text):
            return Intent.CALL_ME
        if self._PRICE.search(text):
            return Intent.PRICE
        if self._DETAILS.search(text):
            return Intent.DETAILS
        if self._LATER.search(text):
            return Intent.LATER
        if self._YES.search(text):
            return Intent.YES
        if self._NO.search(text):
            return Intent.NO
        if self._QUESTION.search(text):
            return Intent.QUESTION

        return Intent.UNKNOWN


intent_classifier = IntentClassifier()
