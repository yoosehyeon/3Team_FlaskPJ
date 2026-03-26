import requests
import traceback

def test_elevators():
    print("Testing /api/elevators...")
    try:
        res = requests.get("http://127.0.0.1:5000/api/elevators", timeout=5)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text[:500]}")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test_elevators()
