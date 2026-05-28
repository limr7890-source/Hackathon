"""Debug: check snapshot status and try different download approaches."""
import httpx
import time

API_KEY = "c755ca2c-f0c7-478d-bcb0-750606dda714"
SNAPSHOT_ID = "snap_mpq2kkw22o582fpmi1"  # from the filter request above

headers = {"Authorization": f"Bearer {API_KEY}"}

with httpx.Client(timeout=30) as client:
    # Try getting snapshot status
    r = client.get(
        f"https://api.brightdata.com/datasets/snapshot/{SNAPSHOT_ID}",
        headers=headers
    )
    print(f"Status endpoint (no params): {r.status_code}")
    print(f"Body: {r.text[:500]}")
    print()

    # Try with format=json
    r2 = client.get(
        f"https://api.brightdata.com/datasets/snapshot/{SNAPSHOT_ID}",
        headers=headers,
        params={"format": "json"}
    )
    print(f"Status endpoint (format=json): {r2.status_code}")
    print(f"Body: {r2.text[:500]}")
    print()

    # Try the download endpoint
    r3 = client.get(
        f"https://api.brightdata.com/datasets/snapshot/{SNAPSHOT_ID}/download",
        headers=headers
    )
    print(f"Download endpoint: {r3.status_code}")
    print(f"Body: {r3.text[:500]}")
