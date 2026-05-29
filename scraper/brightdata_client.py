"""BrightData client module for fetching Instagram posts via the Scrape API."""

import time
from typing import List, Dict, Set, Optional

import httpx

# BrightData scrape endpoint (fast, reliable)
BRIGHTDATA_SCRAPE_URL = "https://api.brightdata.com/datasets/v3/scrape"

# Dataset ID for Instagram posts
IG_POSTS_DATASET_ID = "gd_lk5ns7kz21pck8jpis"


class RateLimiter:
    """Throttles requests to respect BrightData rate limits."""

    def __init__(self, max_requests_per_minute: int = 70):
        """
        Initialize rate limiter.
        
        Args:
            max_requests_per_minute: Maximum number of requests allowed per minute
        """
        self.max_requests_per_minute = max_requests_per_minute
        self._request_timestamps: List[float] = []
        self._window_seconds: float = 60.0

    def acquire(self) -> None:
        """Wait if necessary to respect rate limits, then allow request."""
        while True:
            now = time.time()
            self._request_timestamps = [
                ts for ts in self._request_timestamps
                if now - ts < self._window_seconds
            ]
            if len(self._request_timestamps) < self.max_requests_per_minute:
                 return
            oldest = self._request_timestamps[0]
            sleep_duration = self._window_seconds - (now - oldest)
            if sleep_duration > 0:
                time.sleep(sleep_duration)

    def on_rate_limit_signal(self, reset_time: float) -> None:
        """
        Handle rate limit signal from API.
        
        Args:
            reset_time: Seconds to wait before retrying
        """
        if reset_time > 0:
            time.sleep(reset_time)


class BrightDataClient:
    """
    Client for fetching Instagram posts via BrightData API.
    
    Supports:
    - Fetching posts by URL
    - Searching posts by user + hashtags + date range
    - Searching posts by hashtags + date range
    """

    def __init__(
        self, 
        api_key: str, 
        dataset_id: str = IG_POSTS_DATASET_ID,
        rate_limit: int = 15,
        timeout: float = 120.0
    ):
        """
        Initialize BrightData client.
        
        Args:
            api_key: BrightData API key
            dataset_id: Dataset ID for Instagram posts
            rate_limit: Maximum requests per minute
               self._request_timestamps.append(now)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.dataset_id = dataset_id
        self.rate_limiter = RateLimiter(rate_limit)
        self.timeout = timeout

    def fetch_posts(self, urls: List[str]) -> List[Dict]:
        """
        Fetch Instagram posts by URL using the /scrape endpoint.
        
        Args:
            urls: List of Instagram post URLs
            
        Returns:
            List of post dictionaries (deduplicated by post_id)
            
        Raises:
            RuntimeError: If API request fails
        """
        if not urls:
            return []

        all_posts: List[Dict] = []
        seen_ids: Set[str] = set()

        with httpx.Client(timeout=self.timeout) as client:
            for url in urls:
                try:
                    posts = self._scrape_by_url(client, url)
                    for post in posts:
                        post_id = post.get("post_id", "") or post.get("pk", "") or post.get("id", "")
                        if post_id and post_id not in seen_ids:
                            seen_ids.add(post_id)
                            all_posts.append(post)
                except Exception as e:
                    print(f"Warning: Failed to fetch {url}: {e}")
                    continue

        return all_posts

    def search_by_user_and_hashtags(
        self, 
        username: str, 
        hashtags: List[str],
        start_date: str = "", 
        end_date: str = ""
    ) -> List[Dict]:
        """
        Search for posts from a specific user containing target hashtags within a date range.

        Args:
            username: Instagram username to search
            hashtags: List of hashtags to filter by (with or without # prefix)
            start_date: Start date in DD.MM.YYYY format (optional)
            end_date: End date in DD.MM.YYYY format (optional)

        Returns:
            List of matching posts
            
        Example:
            >>> client.search_by_user_and_hashtags(
            ...     username="cocacola",
            ...     hashtags=["#FIFAWorldCup26", "#TrophyTour"],
            ...     start_date="1.12.2025",
            ...     end_date="1.4.2025"
            ... )
        """
        if not username or not hashtags:
            return []

        # Build search URL for user profile
        user_url = f"https://www.instagram.com/{username}/"
        
        # Add date filters if provided
        filters = {}
        if start_date:
            filters["date_from"] = start_date
        if end_date:
            filters["date_to"] = end_date
        
        try:
            posts = self._scrape_with_filters(user_url, filters)
            
            # Filter posts by hashtags
            normalized_hashtags = {
                h.strip().lower() if h.startswith("#") else f"#{h.strip().lower()}" 
                for h in hashtags
            }
            
            filtered_posts = []
            for post in posts:
                post_hashtags = post.get("hashtags") or post.get("post_hashtags") or []
                post_tags_lower = {h.strip().lower() for h in post_hashtags}
                
                # Check if any target hashtag is in the post
                if any(tag in post_tags_lower for tag in normalized_hashtags):
                    filtered_posts.append(post)
            
            return filtered_posts
        except Exception as e:
            print(f"Warning: Failed to search user {username}: {e}")
            return []

    def search_by_hashtags(
        self, 
        hashtags: List[str], 
        start_date: str = "", 
        end_date: str = ""
    ) -> Dict[str, List[Dict]]:
        """
        Search for all posts containing target hashtags within a date range.

        Args:
            hashtags: List of hashtags to search for (with or without # prefix)
            start_date: Start date in DD.MM.YYYY format (optional)
            end_date: End date in DD.MM.YYYY format (optional)

        Returns:
            Dict mapping each hashtag to a list of matching posts
            
        Example:
            >>> client.search_by_hashtags(
            ...     hashtags=["#FIFAWorldCup26", "#CocaCola"],
            ...     start_date="1.12.2025",
            ...     end_date="1.4.2025"
            ... )
            {
                "#FIFAWorldCup26": [...],
                "#CocaCola": [...]
            }
        """
        if not hashtags:
            return {}

        grouped: Dict[str, List[Dict]] = {}

        for hashtag in hashtags:
            # Normalize hashtag
            tag = hashtag.strip()
            if not tag.startswith("#"):
                tag = f"#{tag}"
            
            # Remove # for URL
            tag_clean = tag[1:] if tag.startswith("#") else tag
            hashtag_url = f"https://www.instagram.com/explore/tags/{tag_clean}/"
            
            print(f"  Searching hashtag: {tag}")
            print(f"    URL: {hashtag_url}")
            print(f"    Date range: {start_date} to {end_date}")
            
            # Build filters with date range
            filters = {}
            if start_date:
                filters["date_from"] = start_date
            if end_date:
                filters["date_to"] = end_date
            
            try:
                posts = self._scrape_with_filters(hashtag_url, filters)
                print(f"    Result: {len(posts)} posts found")
                grouped[hashtag] = posts
            except Exception as e:
                print(f"    Error: {str(e)}")
                grouped[hashtag] = []

        return grouped

    def _scrape_with_filters(self, url: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Internal method to scrape a URL with optional filters.
        
        Args:
            url: URL to scrape
            filters: Optional filters (date_from, date_to, etc.)
            
        Returns:
            List of posts
            
        Raises:
            RuntimeError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        params = {"dataset_id": self.dataset_id, "format": "json"}
        
        payload = [{"url": url, **(filters or {})}]
        
        print(f"    API Request payload: {payload}")

        self.rate_limiter.acquire()
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                BRIGHTDATA_SCRAPE_URL, params=params, headers=headers, json=payload
            )
            
            print(f"    API Response status: {response.status_code}")

            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", "60"))
                print(f"    Rate limited, waiting {retry_after}s...")
                self.rate_limiter.on_rate_limit_signal(retry_after)
                self.rate_limiter.acquire()
                response = client.post(
                    BRIGHTDATA_SCRAPE_URL, params=params, headers=headers, json=payload
                )

            if response.status_code >= 400:
                error_text = response.text[:500]
                print(f"    API Error response: {error_text}")
                raise RuntimeError(
                    f"BrightData error {response.status_code}: {error_text}"
                )

            data = response.json()
            print(f"    API Response type: {type(data)}, length: {len(data) if isinstance(data, list) else 'N/A'}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"    Sample post keys: {list(data[0].keys())[:10]}")
            
            return data if isinstance(data, list) else []

    def _scrape_by_url(self, client: httpx.Client, url: str) -> List[Dict]:
        """
        Fetch a single post using the /scrape endpoint.
        
        Args:
            client: httpx Client instance
            url: Instagram post URL
            
        Returns:
            List of posts (usually 1 post)
            
        Raises:
            RuntimeError: If API request fails
        """
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
