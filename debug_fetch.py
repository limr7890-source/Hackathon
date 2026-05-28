"""Debug script to test a single BrightData Instagram post fetch."""

import os
import sys
import httpx

api_key = os.environ.get("BRIGHTDATA_API_KEY", "c755ca2c-f0c7-478d-bcb0-750606dda714")
if not api_key:
    print("ERROR: Set BRIGHTDATA_API_KEY")
    sys.exit(1)

# Use the exact URL from BrightData's own documentation example
test_url = "https://www.instagram.com/p/Cuf4s0MNqNr"

print(f"Testing with URL: {test_url}")
print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
print("-" * 50)

url = "https://api.brightdata.com/datasets/v3/scrape"
params = {"dataset_id": "gd_lk5ns7kz21pck8jpis", "format": "json"}
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
payload = [{"url": test_url}]

print(f"\nRequest URL: {url}")
print(f"Params: {params}")
print(f"Payload: {payload}")
print()

with httpx.Client(timeout=120.0) as client:
    response = client.post(url, params=params, headers=headers, json=payload)

print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"\nResponse body (first 2000 chars):")
print(response.text[:2000])

# Also show the keys of the first item
import json
data = response.json()
if data:
    print(f"\n\nAll keys in first item:")
    for k in sorted(data[0].keys()):
        print(f"  {k}: {repr(data[0][k])[:100]}")
