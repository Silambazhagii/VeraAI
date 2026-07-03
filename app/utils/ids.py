import uuid


def generate_conversation_id(prefix: str = "conv") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def generate_ack_id(context_id: str, version: int) -> str:
    safe_id = context_id.replace(" ", "_")[:40]
    return f"ack_{safe_id}_v{version}"
