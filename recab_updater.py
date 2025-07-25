import requests
import webbrowser
import os

# Local version
LOCAL_VERSION = "3.10"
VERSION_URL = "https://obi-cmd.github.io/recab-studio/version.json"

try:
    print("🔄 Checking for updates...")
    response = requests.get(VERSION_URL, timeout=5)
    data = response.json()

    if data["version"] != LOCAL_VERSION:
        print(f"🆕 New version available: {data['version']}")
        print(f"Changelog: {data.get('changelog', 'No changelog provided.')}")
        print("Opening download page...")
        webbrowser.open(data["download_url"])
    else:
        print("✅ You are using the latest version: Recab Studio 3.10")

except Exception as e:
    print(f"⚠️ Could not check for updates: {e}")
