# Vera Frontend

Premium React dashboard for the Magicpin AI Bot backend.

## Quick Start

```bash
# Terminal 1 — backend
cd ..
uvicorn main:app --reload --port 8080

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Environment

Copy `.env.example` to `.env`:

```env
VITE_API_BASE_URL=
VITE_API_PROXY_TARGET=http://127.0.0.1:8080
```

Leave `VITE_API_BASE_URL` empty to use the Vite dev proxy (recommended).

For production, set `VITE_API_BASE_URL` to your deployed backend URL.

## Features

- **Dashboard** — merchant selection, health status, context counts
- **Chat** — WhatsApp-style Vera conversation with quick replies
- **Trigger Simulator** — load contexts and fire triggers via `/v1/tick`
- **Merchant Context Panel** — performance, subscription, signals
- **About** — live metadata from `/v1/metadata`

## Stack

React · TypeScript · Vite · Tailwind CSS · shadcn-style UI · Framer Motion · React Query · Sonner
