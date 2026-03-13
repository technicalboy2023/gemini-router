from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import requests
import time
import json
import threading
import logging
import os
from dotenv import load_dotenv

app = FastAPI()

# ===== LOAD ENV =====
load_dotenv()

# ===== DEFAULT MODEL =====
DEFAULT_MODEL = "gemini-2.5-flash"

# ===== API KEYS FROM ENV =====
GEMINI_KEYS = [
os.getenv("GEMINI_KEY_1"),
os.getenv("GEMINI_KEY_2"),
os.getenv("GEMINI_KEY_3"),
os.getenv("GEMINI_KEY_4"),
os.getenv("GEMINI_KEY_5"),
os.getenv("GEMINI_KEY_6"),
os.getenv("GEMINI_KEY_7"),
os.getenv("GEMINI_KEY_8"),
os.getenv("GEMINI_KEY_9"),
os.getenv("GEMINI_KEY_10")
]

# remove empty keys
GEMINI_KEYS = [k for k in GEMINI_KEYS if k]

MAX_RETRIES = 5
TIMEOUT = 120
USAGE_FILE = "usage.json"

lock = threading.Lock()
cooldown = {}

session = requests.Session()

logging.basicConfig(
    filename="router.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# ===== LOAD USAGE =====
if os.path.exists(USAGE_FILE):
    try:
        with open(USAGE_FILE) as f:
            usage = json.load(f)
    except:
        usage = {}
else:
    usage = {}

for k in GEMINI_KEYS:
    usage.setdefault(k,0)

last_save = time.time()


def save_usage():

    global last_save

    if time.time() - last_save < 30:
        return

    try:
        with open(USAGE_FILE,"w") as f:
            json.dump(usage,f)
    except:
        pass

    last_save = time.time()


# ===== PROMPT BUILDER =====
def build_prompt(messages):

    prompt = ""

    for m in messages:

        role = m.get("role","user")
        content = m.get("content","")

        prompt += f"{role}: {content}\n"

    return prompt


# ===== KEY SELECTION =====
def get_available_keys():

    keys = []

    for k in GEMINI_KEYS:

        if k in cooldown and time.time() < cooldown[k]:
            continue

        keys.append(k)

    keys.sort(key=lambda x: usage.get(x,0))

    return keys


# ===== SAFE PARSE =====
def extract_text(data):

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return None


# ===== GEMINI REQUEST =====
def call_gemini(messages,model):

    prompt = build_prompt(messages)

    payload = {
        "contents":[
            {
                "parts":[{"text":prompt}]
            }
        ]
    }

    keys = get_available_keys()

    for key in keys:

        for attempt in range(MAX_RETRIES):

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

            try:

                r = session.post(url,json=payload,timeout=TIMEOUT)

                if r.status_code == 200:

                    data = r.json()

                    text = extract_text(data)

                    if text:

                        with lock:
                            usage[key] += 1
                            save_usage()

                        return text

                if r.status_code in [429,403]:

                    cooldown[key] = time.time() + 10
                    logging.warning(f"Key cooldown")

                    break

                if r.status_code >= 500:

                    continue

            except Exception as e:

                logging.error(e)

                continue

    return "All Gemini API keys exhausted."


# ===== STREAMING =====
def stream_text(text,model):

    words = text.split()

    for w in words:

        chunk = {
            "id":"chatcmpl-stream",
            "object":"chat.completion.chunk",
            "created":int(time.time()),
            "model":model,
            "choices":[
                {
                    "index":0,
                    "delta":{"content":w+" "},
                    "finish_reason":None
                }
            ]
        }

        yield f"data: {json.dumps(chunk)}\n\n"

        time.sleep(0.02)

    end = {
        "id":"chatcmpl-stream",
        "object":"chat.completion.chunk",
        "created":int(time.time()),
        "model":model,
        "choices":[
            {
                "index":0,
                "delta":{},
                "finish_reason":"stop"
            }
        ]
    }

    yield f"data: {json.dumps(end)}\n\n"
    yield "data: [DONE]\n\n"


# ===== CHAT =====
@app.post("/v1/chat/completions")
async def chat(data:dict):

    messages = data.get("messages",[])
    stream = data.get("stream",False)
    model = data.get("model",DEFAULT_MODEL)

    if not model.startswith("gemini"):
        model = DEFAULT_MODEL

    logging.info(f"Request model: {model}")

    reply = call_gemini(messages,model)

    if stream:
        return StreamingResponse(stream_text(reply,model),media_type="text/event-stream")

    return {
        "id":"chatcmpl-"+str(int(time.time())),
        "object":"chat.completion",
        "created":int(time.time()),
        "model":model,
        "choices":[
            {
                "index":0,
                "message":{
                    "role":"assistant",
                    "content":reply
                },
                "finish_reason":"stop"
            }
        ]
    }


# ===== MODELS LIST =====
@app.get("/v1/models")
async def models():

    try:

        key = GEMINI_KEYS[0]

        r = session.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
            timeout=20
        )

        if r.status_code == 200:

            data = r.json()

            models = []

            for m in data.get("models",[]):

                name = m.get("name","")

                model_id = name.replace("models/","")

                models.append({
                    "id":model_id,
                    "object":"model",
                    "owned_by":"google"
                })

            return {
                "object":"list",
                "data":models
            }

    except:
        pass

    return {
        "object":"list",
        "data":[]
    }


# ===== HEALTH =====
@app.get("/health")
async def health():

    return {
        "status":"ok",
        "keys":len(GEMINI_KEYS),
        "usage":usage
    }


# ===== USAGE =====
@app.get("/usage")
async def get_usage():

    return usage
