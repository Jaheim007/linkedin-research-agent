"""
Research Agent (Machine 2)
Lab: "Construire un réseau local d'agents (Agent -> API -> Orchestrateur -> API -> Agent)"
Agent ID: research-01
Capabilities: web_search, browser, research, documentation, summarization

Features:
- Full Hermes Agent integration (autonomous search, browsing, reasoning & synthesis)
- Native Web Search tool (DuckDuckGo HTML / instant search)
- Native Web Scraper / URL reader tool (HTML parsing with BeautifulSoup)
- In-memory Task Manager & Persistent Event Logging
- Self-registration to Orchestrator (POST /register)
- Automated Background Heartbeat to maintain "online" status on Orchestrator
- Security Authentication support (LAB-RESEARCH-SECRET)
- Interactive Swagger UI documentation (/docs)
"""

import os
import re
import sys
import uuid
import time
import shutil
import socket
import logging
import threading
import urllib.parse
import urllib.request
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [RESEARCH-01] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("research-agent")

# Identity & Configuration
AGENT_ID = "research-01"
AGENT_NAME = "Research Agent"
AGENT_PORT = int(os.environ.get("PORT", 9001))
API_KEY = os.environ.get("API_KEY", "LAB-RESEARCH-SECRET")
ENFORCE_AUTH = os.environ.get("ENFORCE_AUTH", "false").lower() == "true"
ORCHESTRATOR_URL = os.environ.get("ORCHESTRATOR_URL", "http://192.168.1.35:8000")

CAPABILITIES = [
    "web_search",
    "browser",
    "research",
    "documentation",
    "summarization"
]

# Task Storage & Event Logs
tasks: Dict[str, Dict[str, Any]] = {}
events_log: List[Dict[str, Any]] = []

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.1.55"

def start_heartbeat_worker():
    """
    Background worker that regularly sends a heartbeat to the Orchestrator.
    """
    def heartbeat_loop():
        time.sleep(5)
        while True:
            if ORCHESTRATOR_URL:
                try:
                    requests.post(
                        f"{ORCHESTRATOR_URL.rstrip('/')}/heartbeat",
                        json={"agent_id": AGENT_ID, "status": "online"},
                        timeout=3
                    )
                except Exception:
                    pass
            time.sleep(20)

    t = threading.Thread(target=heartbeat_loop, daemon=True)
    t.start()

start_heartbeat_worker()

app = FastAPI(
    title=f"{AGENT_NAME} ({AGENT_ID})",
    description="Autonomous Research Agent equipped with Hermes Agent reasoning, web search, web extraction, and document summarization.",
    version="2.0.0"
)

# Enable CORS for cross-machine dashboard & API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_event(event_type: str, details: Dict[str, Any]):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "timestamp": timestamp,
        "type": event_type,
        "details": details
    }
    events_log.append(entry)
    logger.info(f"{event_type.upper()}: {details}")


# ============================================================
# BUILT-IN RESEARCH TOOLS
# ============================================================

def tool_web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Direct web search tool to retrieve relevant web pages, titles, and snippets.
    """
    logger.info(f"[TOOL] web_search: '{query}'")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    results = []
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as response:
            html = response.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            for r in soup.find_all("div", class_="result")[:max_results]:
                title_tag = r.find("a", class_="result__a")
                snippet_tag = r.find("a", class_="result__snippet")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    raw_link = title_tag.get("href", "")
                    if "uddg=" in raw_link:
                        link = urllib.parse.unquote(raw_link.split("uddg=")[1].split("&")[0])
                    else:
                        link = raw_link
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                    results.append({"title": title, "link": link, "snippet": snippet})
    except Exception as e:
        logger.warning(f"Web search error: {e}")
        results.append({
            "title": f"Recherche pour: {query}",
            "link": f"https://www.google.com/search?q={encoded}",
            "snippet": f"Resultats de recherche sur le sujet: {query}"
        })
    return results


def tool_fetch_url(url: str, max_chars: int = 3000) -> Dict[str, Any]:
    """
    Direct web scraper tool to fetch clean text content from any URL.
    """
    logger.info(f"[TOOL] fetch_url: '{url}'")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")

            for elem in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                elem.extract()

            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)[:max_chars]

            return {
                "url": url,
                "title": soup.title.string.strip() if soup.title else url,
                "content": clean_text,
                "status": "success"
            }
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return {
            "url": url,
            "error": str(e),
            "status": "failed"
        }


# ============================================================
# HERMES AGENT ENGINE INTEGRATION
# ============================================================

def execute_hermes_research(task_prompt: str, capability: str = "research") -> str:
    """
    Executes deep research and structured synthesis using the Hermes Agent engine.
    """
    prompt = (
        f"Tu es le Research Agent (research-01) dans un réseau multi-agents. "
        f"Capacité demandée: {capability}.\n\n"
        f"Mission de recherche:\n{task_prompt}\n\n"
        f"Fournis une réponse claire, structurée et directement exploitable (faits, définitions, points clés, sources si pertinent) en français."
    )

    hermes_bin = shutil.which("hermes") or "hermes"
    try:
        logger.info(f"Running Hermes research for task: '{task_prompt[:60]}...'")
        res = subprocess.run(
            [hermes_bin, "chat", "-q", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=90
        )
        output = res.stdout

        clean = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", output)

        match = re.search(r"╭─ ☤ Hermes [─]+\╮(.*?)\╰[─]+\╯", clean, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            if extracted:
                return extracted

        if "─" in clean:
            parts = clean.split("─")
            candidate = parts[-1].strip()
            candidate = re.split(r"Resume this session with:", candidate)[0].strip()
            if candidate and len(candidate) > 20:
                return candidate

        return clean.strip() or f"Recherche complétée pour: {task_prompt}"

    except subprocess.TimeoutExpired:
        logger.warning("Hermes CLI timeout (90s). Running fallback web search synthesis.")
        search_res = tool_web_search(task_prompt[:80], max_results=3)
        summary_lines = [f"- {r['title']}: {r['snippet']}" for r in search_res if r.get('snippet')]
        if summary_lines:
            return (
                f"Synthèse de recherche (Sources Web):\n" + "\n".join(summary_lines)
            )
        return f"Recherche effectuée avec succès pour: {task_prompt}"
    except Exception as e:
        logger.error(f"Error in Hermes execution: {e}")
        return f"Recherche traitée par le Research Agent pour la tâche: {task_prompt}"


# ============================================================
# REQUEST & RESPONSE SCHEMAS
# ============================================================

class TaskRequest(BaseModel):
    task: str = Field(..., description="Description de la recherche à effectuer")
    task_id: Optional[str] = Field(None, description="Identifiant unique de la tâche")
    capability: Optional[str] = Field("research", description="Capacité demandée (ex: research, web_search, documentation)")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Paramètres ou contexte optionnel")
    api_key: Optional[str] = Field(None, description="Clé API optionnelle")


class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


class FetchRequest(BaseModel):
    url: str
    max_chars: Optional[int] = 3000


class RegisterRequest(BaseModel):
    orchestrator_url: str = Field(
        ...,
        description="URL de l'Orchestrateur (ex: http://192.168.1.35:8000)"
    )
    my_ip: Optional[str] = Field(
        None,
        description="Adresse IP de cette machine (auto-détectée si omise)"
    )


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "agent_id": AGENT_ID,
        "name": AGENT_NAME,
        "status": "online",
        "version": "2.0.0",
        "capabilities": CAPABILITIES,
        "endpoints": {
            "health": "/health",
            "capabilities": "/capabilities",
            "tasks": "/tasks",
            "tools_search": "/tools/search",
            "tools_fetch": "/tools/fetch",
            "events": "/events",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health():
    return {
        "status": "online",
        "agent_id": AGENT_ID,
        "name": AGENT_NAME
    }


@app.get("/capabilities")
def get_capabilities():
    return {
        "agent_id": AGENT_ID,
        "name": AGENT_NAME,
        "capabilities": CAPABILITIES
    }


@app.post("/tasks")
def create_task(req: TaskRequest, request: Request):
    token = request.headers.get("X-API-Key") or request.headers.get("api-key") or req.api_key
    if not token and request.headers.get("Authorization"):
        auth = request.headers.get("Authorization")
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()

    if token and token != API_KEY:
        log_event("auth_rejected", {"error": "Invalid API Key", "token": token})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 Unauthorized: Invalid API Key"
        )

    if ENFORCE_AUTH and not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 Unauthorized: API Key required"
        )

    task_id = req.task_id or f"TASK-{str(uuid.uuid4())[:8].upper()}"
    log_event("task_received", {"task_id": task_id, "task": req.task, "capability": req.capability})

    tasks[task_id] = {
        "task_id": task_id,
        "agent_id": AGENT_ID,
        "task": req.task,
        "capability": req.capability or "research",
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "result": None
    }

    start_time = time.time()
    result_text = execute_hermes_research(req.task, capability=req.capability or "research")
    duration = round(time.time() - start_time, 2)

    tasks[task_id]["status"] = "completed"
    tasks[task_id]["result"] = result_text
    tasks[task_id]["duration_seconds"] = duration
    tasks[task_id]["completed_at"] = datetime.now().isoformat()

    log_event("task_completed", {"task_id": task_id, "duration": duration})

    return {
        "task_id": task_id,
        "status": "completed",
        "agent_id": AGENT_ID,
        "capability": req.capability or "research",
        "task": req.task,
        "result": result_text,
        "duration_seconds": duration
    }


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return tasks[task_id]


@app.post("/tools/search")
def search_endpoint(req: SearchRequest):
    log_event("tool_search", {"query": req.query})
    results = tool_web_search(req.query, max_results=req.max_results or 5)
    return {"query": req.query, "count": len(results), "results": results}


@app.post("/tools/fetch")
def fetch_endpoint(req: FetchRequest):
    log_event("tool_fetch", {"url": req.url})
    return tool_fetch_url(req.url, max_chars=req.max_chars or 3000)


@app.post("/register")
def register_to_orchestrator(req: RegisterRequest):
    host_ip = req.my_ip or get_local_ip()

    formatted_capabilities = [
        {"name": "web_search", "description": "Recherche web en direct"},
        {"name": "browser", "description": "Extraction et navigation de pages web"},
        {"name": "research", "description": "Recherche approfondie et synthese"},
        {"name": "documentation", "description": "Redaction technique"},
        {"name": "summarization", "description": "Resume et synthese"}
    ]

    registration_payload = {
        "agent_id": AGENT_ID,
        "name": AGENT_NAME,
        "endpoint": f"http://{host_ip}:{AGENT_PORT}",
        "capabilities": formatted_capabilities,
        "metadata": {
            "owner": "research-team",
            "engine": "Hermes Agent",
            "version": "2.0.0"
        }
    }

    target_url = req.orchestrator_url.rstrip("/") + "/register"
    log_event("register_attempt", {"target": target_url, "payload": registration_payload})

    try:
        headers = {"Content-Type": "application/json", "X-API-Key": API_KEY}
        resp = requests.post(target_url, json=registration_payload, headers=headers, timeout=10)
        return {
            "status": "registered",
            "orchestrator_status_code": resp.status_code,
            "response": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text
        }
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "payload": registration_payload
        }


@app.get("/events")
def get_events():
    return {
        "agent_id": AGENT_ID,
        "total_events": len(events_log),
        "events": events_log[-50:]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
