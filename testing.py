import os
import requests
from dotenv import load_dotenv

load_dotenv()  # ✅ loads environment variables

# -------------------------------
# Query count BIN setup
# -------------------------------
BIN_ID = os.getenv("JSONBIN_BIN_ID")
API_KEY = os.getenv("JSONBIN_API_KEY")
BASE_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

# -------------------------------
# Log BIN setup
# -------------------------------
LOG_BIN_ID = os.getenv("LOG_BIN_ID")
LOG_BASE_URL = f"https://api.jsonbin.io/v3/b/{LOG_BIN_ID}"

HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}


# -------------------------------
# Save query data
# -------------------------------
def save_data(data):
    """Update JSONBin with new query count data."""
    try:
        res = requests.put(BASE_URL, json=data, headers=HEADERS)
        print("📡 Status:", res.status_code)
        print("📡 Response:", res.text[:200])
        return res.status_code in (200, 201)
    except Exception as e:
        print("❌ Error saving data:", e)
        return False


# -------------------------------
# Clear all logs
# -------------------------------
def clear_logs():
    """Completely clear the logs in the log bin."""
    try:
        empty_data = {"logs": []}
        res = requests.put(LOG_BASE_URL, json=empty_data, headers=HEADERS)
        if res.status_code in (200, 201):
            print("🧹 Successfully cleared all logs in JSONBin.")
            return True
        else:
            print(f"⚠️ Failed to clear logs — Status: {res.status_code}")
            print("Response:", res.text[:200])
            return False
    except Exception as e:
        print("❌ Error clearing logs:", e)
        return False


# -------------------------------
# Manual execution
# -------------------------------
if __name__ == "__main__":
    # 🔧 Option 1: manually set the date and count
    manual_date = "2025-10-17"  # change this as needed
    manual_count = 20           # change count value as needed

    data = {
        "query_count": manual_count,
        "last_reset": manual_date
    }

    # success = save_data(data)
    # if success:
    #     print(f"✅ JSONBin updated with date={manual_date} and count={manual_count}")
    # else:
    #     print("❌ Failed to update JSONBin — check credentials or bin permissions.")

    # 🔧 Option 2: uncomment this line if you want to clear all logs
    clear_logs()
