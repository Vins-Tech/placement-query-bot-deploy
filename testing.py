import os
from dotenv import load_dotenv
load_dotenv()  # ✅ loads environment variables
import requests


BIN_ID = os.getenv("JSONBIN_BIN_ID")
API_KEY = os.getenv("JSONBIN_API_KEY")
BASE_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

def save_data(data):
    """Update JSONBin with new data."""
    try:
        res = requests.put(BASE_URL, json=data, headers=HEADERS)
        print("📡 Status:", res.status_code)
        print("📡 Response:", res.text[:200])
        return res.status_code == 200
    except Exception as e:
        print("Error saving data:", e)
        return False


if __name__ == "__main__":
    # 🔧 Manually set the date and count
    manual_date = "2025-10-17"  # change this as needed
    manual_count = 24             # change count value as needed

    data = {
        "query_count": manual_count,
        "last_reset": manual_date
    }

    success = save_data(data)
    if success:
        print(f"✅ JSONBin updated with date={manual_date} and count={manual_count}")
    else:
        print("❌ Failed to update JSONBin — check credentials or bin permissions.")
