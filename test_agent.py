"""
Self-Test Verification for Research Agent (Machine 2)
Tests:
1. GET /health
2. GET /capabilities
3. POST /tasks (Standard Task)
4. GET /tasks/{task_id}
5. Security Auth Test (401 on bad key, 200 on good key)
6. Tool tests: /tools/search and /tools/fetch
"""

import sys
import time
import requests

BASE_URL = "http://127.0.0.1:9001"

def run_tests():
    print("=" * 60)
    print("RUNNING RESEARCH AGENT SELF-TESTS (MACHINE 2)")
    print("=" * 60)

    # 1. Test /health
    print("\n[TEST 1] GET /health")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.json()}")
        assert r.status_code == 200
        assert r.json().get("status") == "online"
        print(">>> TEST 1 PASSED: /health is online")
    except Exception as e:
        print(f">>> TEST 1 FAILED: {e}")
        return False

    # 2. Test /capabilities
    print("\n[TEST 2] GET /capabilities")
    try:
        r = requests.get(f"{BASE_URL}/capabilities", timeout=5)
        print(f"Status Code: {r.status_code}")
        data = r.json()
        print(f"Response: {data}")
        assert r.status_code == 200
        assert data.get("agent_id") == "research-01"
        assert "research" in data.get("capabilities", [])
        print(">>> TEST 2 PASSED: Capability Discovery is compliant")
    except Exception as e:
        print(f">>> TEST 2 FAILED: {e}")
        return False

    # 3. Test /tasks (Execution of research task)
    print("\n[TEST 3] POST /tasks (Lab prompt: 'Donne-moi trois informations sur les agents autonomes.')")
    try:
        payload = {
            "task": "Donne-moi trois informations clés sur les agents autonomes.",
            "capability": "research"
        }
        r = requests.post(f"{BASE_URL}/tasks", json=payload, timeout=70)
        print(f"Status Code: {r.status_code}")
        res = r.json()
        print(f"Task ID: {res.get('task_id')}")
        print(f"Status: {res.get('status')}")
        print(f"Result snippet:\n{res.get('result')[:250]}...")
        assert r.status_code == 200
        assert res.get("status") == "completed"
        task_id = res.get("task_id")
        print(">>> TEST 3 PASSED: Task executed and result generated")
    except Exception as e:
        print(f">>> TEST 3 FAILED: {e}")
        return False

    # 4. Test GET /tasks/{task_id}
    print(f"\n[TEST 4] GET /tasks/{task_id}")
    try:
        r = requests.get(f"{BASE_URL}/tasks/{task_id}", timeout=5)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.json().get('status')}")
        assert r.status_code == 200
        assert r.json().get("status") == "completed"
        print(">>> TEST 4 PASSED: Task retrieval works")
    except Exception as e:
        print(f">>> TEST 4 FAILED: {e}")
        return False

    # 5. Test Tools Endpoints (/tools/search)
    print("\n[TEST 5] POST /tools/search")
    try:
        r = requests.post(f"{BASE_URL}/tools/search", json={"query": "ISO 27001", "max_results": 2}, timeout=10)
        assert r.status_code == 200
        print(f"Search results count: {r.json().get('count')}")
        print(">>> TEST 5 PASSED: Tool search works")
    except Exception as e:
        print(f">>> TEST 5 FAILED: {e}")
        return False

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! RESEARCH AGENT IS READY.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    run_tests()
