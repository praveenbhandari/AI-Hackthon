from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal, Optional
import re
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage

app = FastAPI()

# ---- Claude Model via LangChain ----
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    temperature=0.7,
    max_tokens=1024
)

# ---- Weather Forecast ----
def get_forecast_summary():
    return (
        "Here's the 5-day weather forecast for San Francisco:\n"
        "Mon: 18°C, cloudy — light jacket\n"
        "Tue: 21°C, sunny — T-shirt\n"
        "Wed: 19°C, rainy — umbrella\n"
        "Thu: 22°C, clear — light clothes\n"
        "Fri: 20°C, windy — hoodie\n"
    )

# ---- Chat-like Schema ----
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    model: Optional[str]
    messages: List[Message]
    temperature: Optional[float] = 0.7

# ---- Formatter: Clean for speech ----
def clean_response(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # remove bold markdown
    text = text.replace("\n\n", " ").replace("\n", " ")
    return text.strip()

# ---- Claude-backed POST endpoint ----
@app.post("/v1/chat/completions")
def chat_completions(request: ChatRequest):
    last_user_msg = [m.content for m in request.messages if m.role == "user"][-1]
    print("🗣️ Vapi said:", last_user_msg)

    messages = [
        {
            "role": "system",
            "content": "You are a friendly student weather stylist. Always respond based on the forecast."
        },
        {
            "role": "user",
            "content": f"{get_forecast_summary()}\n\nStudent asked: {last_user_msg}"
        }
    ]

    try:
        raw_response = llm.invoke(messages)

        # Handle all possible formats
        if isinstance(raw_response, AIMessage):
            response_text = raw_response.content
        elif isinstance(raw_response, dict) and "content" in raw_response:
            response_text = raw_response["content"]
        elif isinstance(raw_response, str):
            response_text = raw_response
        else:
            raise ValueError("Unknown response format from Claude")

        cleaned = clean_response(response_text)

    except Exception as e:
        print("❌ Claude error:", e)
        cleaned = "I'm sorry, I couldn't process that. Please try again."

    print("🤖 Claude reply (cleaned):", cleaned)

    return {
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": cleaned
                },
                "finish_reason": "stop"
            }
        ]
    }

# ---- GET endpoint for browser testing ----
@app.get("/v1/chat/completions")
def chat_completions_get():
    return {"status": "OK", "message": "Use POST method with JSON body like OpenAI Chat API"}

# ---- Health check (optional root) ----
@app.get("/")
def root():
    return {"status": "running"}
