Gemini Router

OpenAI-compatible API router for Google Gemini models.
This router allows Gemini models to be used with tools like n8n, OpenAI SDKs, and custom AI agents.

---

Features

- Multiple Gemini API keys
- Automatic key rotation
- Cooldown handling
- Usage tracking
- Streaming responses
- OpenAI compatible endpoints
- n8n AI Agent support
- systemd auto-start support

---

Requirements

- Ubuntu / Debian VPS
- Python 3.9+
- Git
- Internet access

---

Installation (Using Installer Script)

Run the following commands on your VPS:

cd /home/aman
mkdir -p routers
cd routers

curl -O https://raw.githubusercontent.com/technicalboy2023/gemini-router/main/install-router.sh

chmod +x install-router.sh

sed -i 's/\r$//' install-router.sh

bash install-router.sh gemini-router 5000

This will automatically:

- Clone the repository
- Create Python virtual environment
- Install dependencies
- Create systemd service
- Start the router

---

Configure API Keys

Edit the ".env" file:

nano /home/aman/routers/gemini-router/.env

Example:

GEMINI_KEY_1=YOUR_API_KEY
GEMINI_KEY_2=YOUR_API_KEY
GEMINI_KEY_3=
GEMINI_KEY_4=

Restart router:

sudo systemctl restart gemini-router

---

API Endpoints

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

Check Router Status

systemctl status gemini-router

---

Router Logs

journalctl -u gemini-router -f

---

License

MIT
