"""
🌐 API SERVER — Bọc app.py / mcp_server.py / providers.py bằng FastAPI
Không thay đổi logic gốc, chỉ mở HTTP endpoint để frontend (HTML/CSS/JS) gọi được.

Chạy: uvicorn server:app --reload --port 8000
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import run_react_agent, run_baseline_chatbot, load_test_cases
from mcp_server import MCPHealthServer
from providers import get_llm_provider, MockOfflineProvider, GeminiProvider, OpenAIProvider

app = FastAPI(title="Vinmec Agent Lab API")

# Cho phép frontend (mở trực tiếp file HTML hoặc chạy Live Server) gọi được
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo 1 lần khi server start
provider = get_llm_provider()
mcp_server = MCPHealthServer()


class QueryRequest(BaseModel):
    query: str


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "provider": provider.__class__.__name__,
        "mcp_server": mcp_server.server_name,
    }


@app.get("/api/tools")
def list_tools():
    """Danh sách tools mà MCP Server công bố"""
    return mcp_server.list_tools()


@app.get("/api/test-cases")
def get_test_cases():
    """Danh sách 5 test case mẫu từ config/test_cases.json"""
    return load_test_cases()


@app.post("/api/chat")
def chat_baseline(req: QueryRequest):
    """Chatbot Baseline — không có tool"""
    from prompts import CHATBOT_BASELINE_PROMPT
    response = provider.generate(req.query, system_prompt=CHATBOT_BASELINE_PROMPT)
    return {"query": req.query, "response": response}


@app.post("/api/agent")
def agent_run(req: QueryRequest):
    """ReAct Agent — trả về toàn bộ trace log (Thought/Action/Observation/Final Answer)"""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống.")
    logs = run_react_agent(req.query, provider, mcp_server)
    return {"query": req.query, "trace": logs}


@app.get("/api/trace-waterfall")
def get_trace_waterfall():
    """Đọc lại docs/trace_waterfall.json (nếu có) để vẽ biểu đồ latency"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    trace_path = os.path.join(base_dir, "docs", "trace_waterfall.json")
    if not os.path.exists(trace_path):
        return []
    with open(trace_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/provider/{provider_name}")
def switch_provider(provider_name: str):
    """Đổi provider ngay trên UI mà không cần sửa .env / restart server"""
    global provider
    mapping = {
        "mock": MockOfflineProvider,
        "gemini": GeminiProvider,
        "openai": OpenAIProvider,
    }
    cls = mapping.get(provider_name.lower())
    if not cls:
        raise HTTPException(status_code=400, detail=f"Provider '{provider_name}' không hợp lệ.")
    provider = cls()
    return {"provider": provider.__class__.__name__}
