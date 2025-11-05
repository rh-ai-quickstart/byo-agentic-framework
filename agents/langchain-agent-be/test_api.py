"""
Simple test script for the FastAPI LangChain 1.0 Agent backend

Usage:
    python test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def test_config():
    """Test config endpoint"""
    print("Testing /config endpoint...")
    response = requests.get(f"{BASE_URL}/config")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def test_tools():
    """Test tools endpoint"""
    print("Testing /tools endpoint...")
    response = requests.get(f"{BASE_URL}/tools")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def test_ask_simple():
    """Test simple ask endpoint"""
    print("Testing /ask/simple endpoint...")
    query = "What's the weather in Boston?"
    response = requests.post(
        f"{BASE_URL}/ask/simple",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    print(f"Query: {query}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.status_code == 200

def test_ask_detailed():
    """Test detailed ask endpoint"""
    print("Testing /ask endpoint (detailed)...")
    query = "What's the weather in Miami?"
    response = requests.post(
        f"{BASE_URL}/ask",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )
    print(f"Query: {query}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Query: {result['query']}")
        print(f"Messages count: {len(result['messages'])}")
        print(f"Final response: {result['final_response'][:200]}...\n")
    else:
        print(f"Error: {response.text}\n")

    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 60)
    print("FastAPI LangChain 1.0 Agent - API Tests")
    print("=" * 60 + "\n")

    tests = [
        ("Health Check", test_health),
        ("Configuration", test_config),
        ("Tools List", test_tools),
        ("Simple Ask", test_ask_simple),
        ("Detailed Ask", test_ask_detailed),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "PASS" if success else "FAIL"))
        except requests.exceptions.ConnectionError:
            print(f"ERROR: Could not connect to {BASE_URL}")
            print("Make sure the server is running: python app.py\n")
            results.append((test_name, "ERROR"))
            break
        except Exception as e:
            print(f"ERROR in {test_name}: {str(e)}\n")
            results.append((test_name, "ERROR"))

    # Print summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()
