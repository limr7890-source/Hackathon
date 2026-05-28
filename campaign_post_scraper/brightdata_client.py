"""BrightData client module for fetching X posts via the Dataset API."""

import csv
import io
import time

import httpx

# BrightData Dataset API endpoint
BRIGHTDATA_SCRAPE_URL = "https://api.brightdata.com/datasets/v3/scrape"

# Dataset ID for X (Twitter) posts
X_POSTS_DATASET_ID = "gd_lwxkxvnf1cynvib9co"


class RateLimiter:
    """Throttles requests to respect BrightData rate limits."""

    def __init__(self, max_requests_per_minute: int = 50):
        """
        Initialize the rate limiter.

        Args:
            max_requests_per_minute: Maximum number of requests allowed per minute.
        """
        self.max_requests_per_minute = max_requests_per_minute
        self._request_timestamps: list[float] = []
        self._window_seconds: float = 60.0

    def acquire(self) -> None:
        """Blocks until a request slot is available."""
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
        """
        Pauses until the rate limit window resets.

        Args:
            reset_time: Time in seconds to wait before resuming.
        """
        if reset_time > 0:
            time.sleep(reset_time)


class BrightDataClient:
    """Client for fetching X post data from BrightData's Dataset API."""

    def __init__(self, api_key: str, dataset_id: str = X_POSTS_DATASET_ID,
                 rate_limit: int = 15):
        """
        Initialize the BrightData client.

        Args:
            api_key: API key (Bearer token) for BrightData.
            dataset_id: The dataset ID to query (default: X posts).
            rate_limit: Maximum requests per minute (default 15).
        """
        self.api_key = api_key
        self.dataset_id = dataset_id
        self.rate_limiter = RateLimiter(rate_limit)

    def fetch_posts(self, urls: list[str]) -> list[dict]:
        """
        Fetch post data from BrightData, one URL at a time.

        Deduplicates results by 'id' field.
        Raises on any error (no retries except for 429).

        Args:
            urls: List of X post URLs to fetch.

        Returns:
            A deduplicated list of post dicts.
        """
        if not urls:
            return []

        all_posts: list[dict] = []
        seen_ids: set[str] = set()

        with httpx.Client(timeout=120.0) as client:
            for url in urls:
                response = self._send_request(client, url)
                posts = self._parse_response(response)

                for post in posts:
                    post_id = post.get("id", "")
                    if post_id and post_id not in seen_ids:
                        seen_ids.add(post_id)
                        all_posts.append(post)

        return all_posts

    def _send_request(self, client: httpx.Client, url: str) -> httpx.Response:
        """
        Send a single URL to BrightData Dataset API with rate limiting.

        Handles 429 rate limit responses by pausing and retrying once.
        Raises immediately on any other error.
        """
        params = {
            "dataset_id": self.dataset_id,
            "format": "json",
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
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
                f"BrightData API error {response.status_code}: {response.text}"
            )
        return response

    def _parse_response(self, response: httpx.Response) -> list[dict]:
        """Parse the JSON response into a list of post dicts."""
        data = response.json()
        if isinstance(data, list):
            return data
        return []
