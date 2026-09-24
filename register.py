"""
Registration Helper Script for Machine 2 (Research Agent)
Usage:
    python register.py <ORCHESTRATOR_URL> [MY_IP]
Example:
    python register.py http://192.168.1.35:8000
"""

import sys
import socket
import json
import requests

AGENT_ID = "research-01"
AGENT_NAME = "Research Agent"
AGENT_PORT = 9001
API_KEY = "LAB-RESEARCH-SECRET"
CAPABILITIES = [
    {"name": "web_search", "description": "Recherche web en direct"},
    {"name": "browser", "description": "Extraction et navigation de pages web"},
    {"name": "research", "description": "Recherche approfondie, faits et synthese"},
    {"name": "documentation", "description": "Redaction technique et matrices comparatives"},
    {"name": "summarization", "description": "Resume et synthese analytique"}
]

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.1.55"

def main():
    if len(sys.argv) < 2:
        print("Usage: python register.py <ORCHESTRATOR_URL> [MY_IP]")
        print("Example: python register.py http://192.168.1.35:8000")
        sys.exit(1)

    orchestrator_url = sys.argv[1].rstrip("/")
    my_ip = sys.argv[2] if len(sys.argv) > 2 else get_local_ip()

    payload = {
        "agent_id": AGENT_ID,
        "name": AGENT_NAME,
        "endpoint": f"http://{my_ip}:{AGENT_PORT}",
        "capabilities": CAPABILITIES,
        "metadata": {
            "owner": "research-team",
            "engine": "Hermes Agent",
            "version": "2.0.0"
        }
    }

    target = f"{orchestrator_url}/register"
    print(f"[*] Registering {AGENT_ID} to {target}...")
    print(f"[*] Payload:\n{json.dumps(payload, indent=2)}")

    try:
        headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
        res = requests.post(target, json=payload, headers=headers, timeout=10)
        print(f"[+] Status Code: {res.status_code}")
        print(f"[+] Response: {res.text}")
    except Exception as e:
        print(f"[-] Registration failed: {e}")

if __name__ == "__main__":
    main()
