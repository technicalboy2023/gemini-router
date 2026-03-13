Gemini Router

OpenAI-compatible router for Google Gemini models.
This router allows using Gemini models with tools like n8n, OpenAI SDKs, and custom applications.

Features

- Multiple API key support
- Automatic key rotation
- Cooldown handling
- Usage tracking
- Streaming support
- OpenAI compatible API
- Works with n8n AI Agent

---

Installation

Clone the repository:

git clone https://github.com/technicalboy2023/gemini-router.git
cd gemini-router

Create virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install fastapi uvicorn requests python-dotenv

---

Environment Variables

Create ".env" file:

GEMINI_KEY_1=YOUR_KEY
GEMINI_KEY_2=YOUR_KEY
GEMINI_KEY_3=
GEMINI_KEY_4=
GEMINI_KEY_5=
GEMINI_KEY_6=
GEMINI_KEY_7=
GEMINI_KEY_8=
GEMINI_KEY_9=
GEMINI_KEY_10=

---

Run Router

uvicorn router:app --host 0.0.0.0 --port 5000

---

Endpoints

Chat

POST /v1/chat/completions

Example:

curl http://localhost:5000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
"model":"gemini-2.5-flash",
"messages":[{"role":"user","content":"hello"}]
}'

---

Models

GET /v1/models

---

Health

GET /health

---

Usage

GET /usage

---

n8n Setup

Base URL:

http://VPS_IP:5000/v1

Model example:

gemini-2.5-flash

---

License

MIT
