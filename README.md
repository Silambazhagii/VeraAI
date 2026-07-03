# Magicpin AI Bot

Intelligent AI Merchant Assistant backend for the **Magicpin AI Challenge**. This REST API receives structured contexts from the judge harness, decides when to send proactive WhatsApp-style messages, and continues multi-turn conversations with merchants and customers.

## Approach

- **Rule Engine + Context Store + Mock LLM** — deterministic decision logic with template-based message composition (no external LLM calls)
- **Clean Architecture** — separated API, services, and models layers
- **In-memory state** — thread-safe context store and conversation manager

## Requirements

- Python 3.11+
- pip

## Installation

```bash
cd magicpin-ai-bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running Locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

API docs: http://localhost:8080/docs

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TEAM_NAME` | Magicpin Challenge | Team name in metadata |
| `CONTACT_EMAIL` | example@email.com | Contact email |
| `MODEL_NAME` | Context Aware Merchant AI | Model label |
| `APPROACH` | Rule Engine + Context Store + Mock LLM | Approach description |
| `APP_VERSION` | 1.0 | API version |
| `LOG_LEVEL` | INFO | Logging level |

Copy `.env.example` to `.env` and customize as needed.

## Folder Structure

```
magicpin-ai-bot/
├── app/
│   ├── api/              # FastAPI routers (health, metadata, context, tick, reply)
│   ├── core/             # Config and logging
│   ├── models/           # Pydantic domain + API models
│   ├── services/         # Business logic (store, engine, composer, classifier)
│   └── utils/            # Helpers and ID generation
├── tests/                # pytest suite
├── dataset/              # Challenge dataset (copy from challenge package)
├── main.py               # Application entry point
├── requirements.txt
└── README.md
```

## API Endpoints

### GET /v1/healthz

Liveness probe with uptime and loaded context counts.

### GET /v1/metadata

Bot identity and approach metadata.

### POST /v1/context

Push category, merchant, customer, or trigger context with version control.

### POST /v1/tick

Periodic wake-up — bot inspects available triggers and returns proactive actions.

### POST /v1/reply

Receive merchant/customer reply and return next assistant action (`send`, `wait`, or `end`).

## Testing

```bash
pytest tests/ -v
```

## Deployment (Render)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your Git repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (`TEAM_NAME`, `CONTACT_EMAIL`, etc.)
6. Deploy and submit the public URL to the challenge portal

Alternatively, add a `render.yaml`:

```yaml
services:
  - type: web
    name: magicpin-ai-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: TEAM_NAME
        value: Magicpin Challenge
      - key: CONTACT_EMAIL
        value: example@email.com
```

## Example curl Requests

```bash
export BOT_URL=http://localhost:8080

# Health
curl $BOT_URL/v1/healthz

# Metadata
curl $BOT_URL/v1/metadata

# Push category context
curl -X POST $BOT_URL/v1/context \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "category",
    "context_id": "dentists",
    "version": 1,
    "delivered_at": "2026-04-26T10:00:00Z",
    "payload": {"slug": "dentists", "voice": {"tone": "peer_clinical"}, "peer_stats": {"avg_ctr": 0.03}, "digest": []}
  }'

# Tick
curl -X POST $BOT_URL/v1/tick \
  -H "Content-Type: application/json" \
  -d '{"now": "2026-04-26T10:35:00Z", "available_triggers": ["trg_001_research_digest_dentists"]}'

# Reply
curl -X POST $BOT_URL/v1/reply \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "merchant_id": "m_001_drmeera_dentist_delhi",
    "from_role": "merchant",
    "message": "Yes please send the abstract",
    "received_at": "2026-04-26T10:42:00Z",
    "turn_number": 2
  }'
```

## License

Challenge submission — not for production merchant outreach.
# VeraAI
