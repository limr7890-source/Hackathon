"""BrightData client module for executing scrape queries and handling rate limiting."""

import csv
import io
import time

import httpx


class RateLimiter:
    """Throttles requests to respect BrightData rate limits."""

    def __init__(self, max_requests_per_minute: int = 30):
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
    """Client for sending queries to BrightData and parsing CSV responses."""

    def __init__(self, api_key: str, base_url: str, rate_limit: int = 30):
        """
        Initialize the BrightData client.

        Args:
            api_key: API key for authenticating with BrightData.
            base_url: Base URL of the BrightData API.
            rate_limit: Maximum requests per minute (default 30).
        """
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limiter = RateLimiter(rate_limit)

    def execute_queries(self, queries: list[dict]) -> list[dict]:
        """
        Sends each query to BrightData, parses CSV responses into a list of dicts.
        Deduplicates by 'id' field across all query responses.
        Raises on any error (no retries).

        Args:
            queries: List of query dicts to execute.

        Returns:
            A deduplicated list of post dicts from BrightData CSV responses.
        """
        all_posts: list[dict] = []
        seen_ids: set[str] = set()

        with httpx.Client() as client:
            for query in queries:
                response = self._send_request(client, query)
                posts = self._parse_csv_response(response.text)

                for post in posts:
                    post_id = post.get("id", "")
                    if post_id and post_id not in seen_ids:
                        seen_ids.add(post_id)
                        all_posts.append(post)

        return all_posts

    def _send_request(self, client: httpx.Client, query: dict) -> httpx.Response:
        """
        Send a single query to BrightData with rate limiting.

        Handles 429 rate limit responses by pausing and retrying once.
        Raises immediately on any other error.
        """
        url = f"{self.base_url}/search"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        self.rate_limiter.acquire()
        response = client.post(url, json=query, headers=headers)

        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", "60"))
            self.rate_limiter.on_rate_limit_signal(retry_after)
            self.rate_limiter.acquire()
            response = client.post(url, json=query, headers=headers)

        response.raise_for_status()
        return response

    def _parse_csv_response(self, csv_text: str) -> list[dict]:
        """Parse a CSV response string into a list of dicts."""
        reader = csv.DictReader(io.StringIO(csv_text))
        return list(reader)
