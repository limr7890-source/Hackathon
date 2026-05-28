"""Find a user with multiple posts using the discover-by-username endpoint."""
import httpx

API_KEY = "c755ca2c-f0c7-478d-bcb0-750606dda714"

print("Fetching tinybaki's posts via discover endpoint...")
r = httpx.Client(timeout=120).post(
    "https://api.brightdata.com/datasets/v3/scrape",
    params={
        "dataset_id": "gd_l1vikfch901nx3by4",
        "type": "discover_new",
        "discover_by": "user_name",
        "format": "json",
    },
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json=[{"user_name": "tinybaki"}],
)
print(f"Status: {r.status_code}")
d = r.json()
if not d:
    print("Empty response")
    exit()

posts = d[0].get("posts", []) if isinstance(d, list) else []
print(f"Total posts: {len(posts)}")

# Find posts with #tattoo
tattoo_posts = [p for p in posts if "tattoo" in [t.lower() for t in (p.get("post_hashtags") or [])]]
print(f"Posts with 'tattoo' hashtag: {len(tattoo_posts)}")

for p in tattoo_posts[:5]:
    print(f"  URL: {p.get('url')}")
    print(f"  Hashtags: {(p.get('post_hashtags') or [])[:5]}")
    print()

# Also show all unique hashtags across posts
all_tags = set()
for p in posts:
    for t in (p.get("post_hashtags") or []):
        all_tags.add(t.lower())
print(f"All unique hashtags ({len(all_tags)}):")
for t in sorted(list(all_tags))[:20]:
    count = sum(1 for p in posts if t in [x.lower() for x in (p.get("post_hashtags") or [])])
    if count > 1:
        print(f"  {t}: {count} posts")
