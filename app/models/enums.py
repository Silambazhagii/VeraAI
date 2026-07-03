from enum import Enum


class ContextScope(str, Enum):
    CATEGORY = "category"
    MERCHANT = "merchant"
    CUSTOMER = "customer"
    TRIGGER = "trigger"


class TriggerKind(str, Enum):
    RESEARCH_DIGEST = "research_digest"
    RENEWAL_DUE = "renewal_due"
    RECALL_DUE = "recall_due"
    FESTIVAL = "festival"
    FESTIVAL_UPCOMING = "festival_upcoming"
    REVIEW_REQUEST = "review_request"
    REVIEW_THEME_EMERGED = "review_theme_emerged"
    REGULATION_CHANGE = "regulation_change"
    PERFORMANCE_DROP = "performance_drop"
    PERF_DIP = "perf_dip"
    CUSTOMER_FOLLOWUP = "customer_followup"
    SUBSCRIPTION_EXPIRY = "subscription_expiry"
    ACTIVE_OFFER = "active_offer"
    CURIOUS_ASK_DUE = "curious_ask_due"
    WINBACK_ELIGIBLE = "winback_eligible"


class Intent(str, Enum):
    YES = "YES"
    NO = "NO"
    CALL_ME = "CALL_ME"
    PRICE = "PRICE"
    DETAILS = "DETAILS"
    STOP = "STOP"
    LATER = "LATER"
    QUESTION = "QUESTION"
    UNKNOWN = "UNKNOWN"
    AUTO_REPLY = "AUTO_REPLY"
    INTERESTED = "INTERESTED"


class ReplyAction(str, Enum):
    SEND = "send"
    WAIT = "wait"
    END = "end"


class SendAs(str, Enum):
    VERA = "vera"
    MERCHANT_ON_BEHALF = "merchant_on_behalf"


class CtaType(str, Enum):
    OPEN_ENDED = "open_ended"
    BINARY_YES_NO = "binary_yes_no"
    BINARY_CONFIRM_CANCEL = "binary_confirm_cancel"
    MULTI_CHOICE_SLOT = "multi_choice_slot"
    NONE = "none"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    WAITING = "waiting"
    ENDED = "ended"


class DecisionPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
