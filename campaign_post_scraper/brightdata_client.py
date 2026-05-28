"""BrightData client module for fetching Instagram posts via the Scrape API."""

import time

import httpx

# BrightData scrape endpoint (fast, reliable)
BRIGHTDATA_SCRAPE_URL = "https://api.brightdata.com/datasets/v3/scrape"

# Dataset ID for Instagram posts
IG_POSTS_DATASET_ID = "gd_lk5ns7kz21pck8jpis"


class RateLimiter:
    """Throttles requests to respect BrightData rate limits."""

    def __init__(self, max_requests_per_minute: int = 15):
        self.max_requests_per_minute = max_requests_per_minute
        self._request_timestamps: list[float] = []
        self._window_seconds: float = 60.0

    def acquire(self) -> None:
        while True:
            now = time.time()
            self._request_timestamps = [
                ts for ts in self._request_timestamps
                if now - ts < self._window_seconds
            ]
            if len(self._request_timestamps) < self.max_requests_per_minute:
                self._request_timestamps.append(now)
                return
            oldest = self._request_timestamps[0]
            sleep_duration = self._window_seconds - (now - oldest)
            if sleep_duration > 0:
                time.sleep(sleep_duration)

    def on_rate_limit_signal(self, reset_time: float) -> None:
        if reset_time > 0:
            time.sleep(reset_time)


class BrightDataClient:
    """Client for fetching Instagram posts by URL."""

    def __init__(self, api_key: str, dataset_id: str = IG_POSTS_DATASET_ID,
                 rate_limit: int = 15):
        self.api_key = api_key
        self.dataset_id = dataset_id
        self.rate_limiter = RateLimiter(rate_limit)

    def fetch_posts(self, urls: list[str]) -> list[dict]:
        """Fetch Instagram posts by URL using the /scrape endpoint."""
        if not urls:
            return []

        all_posts: list[dict] = []
        seen_ids: set[str] = set()

        with httpx.Client(timeout=120.0) as client:
            for url in urls:
                posts = self._scrape_by_url(client, url)
                for post in posts:
                    post_id = post.get("post_id", "") or post.get("pk", "")
                    if post_id and post_id not in seen_ids:
                        seen_ids.add(post_id)
                        all_posts.append(post)

        return all_posts

    def expand_by_hashtags(self, seed_posts: list[dict],
                           target_hashtags: list[str]) -> dict:
        """
        Expand: group fetched posts by target hashtags.

        For each target hashtag, find all seed posts that contain it.
        A post can appear under multiple hashtags.

        Args:
            seed_posts: Posts already fetched via fetch_posts().
            target_hashtags: Hashtags from the CSV Target_Hashtag column.

        Returns:
            Dict mapping each hashtag to a list of matching posts.
        """
        if not target_hashtags:
            return {}

        # Normalize target hashtags
        targets = {}
        for tag in target_hashtags:
            t = tag.strip().lower()
            if not t.startswith("#"):
                t = f"#{t}"
            display = tag if tag.startswith("#") else f"#{tag}"
            targets[t] = display

        grouped: dict[str, list[dict]] = {d: [] for d in targets.values()}

        for post in seed_posts:
            post_hashtags = post.get("hashtags") or []
            post_tags_lower = {h.strip().lower() for h in post_hashtags}

            for norm, display in targets.items():
                if norm in post_tags_lower:
                    grouped[display].append(post)

        return grouped

    def _scrape_by_url(self, client: httpx.Client, url: str) -> list[dict]:
        """Fetch a single post using the /scrape endpoint."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        params = {"dataset_id": self.dataset_id, "format": "json"}
        payload = [{"url": url}]

        self.rate_limiter.acquire()
        response = client.post(
            BRIGHTDATA_SCRAPE_URL, params=params, headers=headers, json=payload
        )

        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", "60"))
            self.rate_limiter.on_rate_limit_signal(retry_after)
            self.rate_limiter.acquire()
            response = client.post(
                BRIGHTDATA_SCRAPE_URL, params=params, headers=headers, json=payload
            )

        if response.status_code >= 400:
            raise RuntimeError(
                f"BrightData error {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        return data if isinstance(data, list) else []
