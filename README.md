# Hotel Reservation Voice Agent 🏨

A real-time voice AI agent that manages hotel reservations via natural conversation. Guests can check, create, modify, and cancel bookings by speaking to the agent over WebRTC, with all changes reflected in a live dashboard.

**Tech Stack**: Pipecat (voice pipeline) + Deepgram STT + OpenAI GPT-4o + Cartesia TTS + Daily.co WebRTC + FastAPI + MongoDB

## Features

- 🎙️ **Voice Interaction**: Natural conversation via WebRTC
- 🔒 **Secure**: Account verification before any database access
- 📊 **Live Dashboard**: Real-time view of reservations at `/dashboard`
- 🛠️ **5 Tools**: Check account, view reservations, create, edit, cancel

## Quick Start

### 1. Start MongoDB
```bash
mongod
```

### 2. Start the Dashboard API
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Dashboard: http://localhost:8000/dashboard

### 3. Start the Voice Agent
```bash
cd reservation_agent_proj/server
cp .env.example .env  # Add your API keys
uv sync
uv run bot.py --transport daily
```
Voice Interface: http://localhost:7860

## Required API Keys

| Key | Service | Get it at |
|-----|---------|-----------|
| `OPENAI_API_KEY` | LLM | [platform.openai.com](https://platform.openai.com) |
| `DEEPGRAM_API_KEY` | Speech-to-Text | [console.deepgram.com](https://console.deepgram.com) |
| `CARTESIA_API_KEY` | Text-to-Speech | [play.cartesia.ai](https://play.cartesia.ai) |
| `DAILY_API_KEY` | WebRTC | [dashboard.daily.co](https://dashboard.daily.co) |

## Project Structure

```
reservation_management/
├── app/
│   ├── main.py          # FastAPI + Dashboard
│   ├── tools.py         # Reservation tools (5 functions)
│   └── database.py      # MongoDB connection + seeding
├── reservation_agent_proj/
│   └── server/
│       ├── bot.py       # Pipecat voice agent
│       └── pyproject.toml
└── requirements.txt
```

## Test Accounts

| Account ID | Guest Name | Reservations |
|------------|------------|--------------|
| 10001 | John Smith | 1 confirmed |
| 10002 | Jane Doe | 1 cancelled |
| 10003 | Test User | None |

## API Endpoints

- `GET /dashboard` - Live reservation dashboard
- `GET /api/accounts` - All accounts (JSON)
- `GET /tools/check_account_status?account_id=10001`
- `GET /tools/get_guest_reservation?account_id=10001&search_name=John`
- `POST /tools/make_new_reservation?...`
- `POST /tools/cancel_guest_reservation?...`
- `PATCH /tools/edit_guest_reservation?...`
