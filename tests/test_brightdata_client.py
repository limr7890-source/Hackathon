"""Tests for the BrightDataClient class."""

from unittest.mock import patch, MagicMock

import httpx
import pytest

from campaign_post_scraper.brightdata_client import BrightDataClient


def _make_csv_response(rows: list[dict], status_code: int = 200, headers: dict = None) -> httpx.Response:
    """Helper to create a mock httpx.Response with CSV content."""
    if not rows:
        csv_text = ""
    else:
        columns = list(rows[0].keys())
        lines = [",".join(columns)]
        for row in rows:
            lines.append(",".join(str(row[col]) for col in columns))
        csv_text = "\n".join(lines)

    response = httpx.Response(
        status_code=status_code,
        text=csv_text,
        headers=headers or {},
        request=httpx.Request("POST", "http://test.com/search"),
    )
    return response


class TestBrightDataClientInit:
    """Tests for BrightDataClient initialization."""

    def test_init_sets_api_key_and_base_url(self):
        client = BrightDataClient(api_key="test-key", base_url="http://api.test.com")
        assert client.api_key == "test-key"
        assert client.base_url == "http://api.test.com"

    def test_init_creates_rate_limiter_with_default(self):
        client = BrightDataClient(api_key="key", base_url="http://api.test.com")
        assert client.rate_limiter.max_requests_per_minute == 30

    def test_init_creates_rate_limiter_with_custom_limit(self):
        client = BrightDataClient(api_key="key", base_url="http://api.test.com", rate_limit=10)
        assert client.rate_limiter.max_requests_per_minute == 10


class TestExecuteQueries:
    """Tests for BrightDataClient.execute_queries()."""

    @patch("campaign_post_scraper.brightdata_client.httpx.Client")
    def test_execute_queries_single_query_returns_posts(self, mock_client_cls):
        """A single query returning CSV data should be parsed into dicts."""
        posts = [
            {"id": "1", "user_posted": "alice", "description": "hello"},
            {"id": "2", "user_posted": "bob", "description": "world"},
        ]
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = _make_csv_response(posts)
        mock_client_cls.return_value = mock_client

        client = BrightDataClient(api_key="key", base_url="http://api.test.com")
        result = client.execute_queries([{"hashtags": ["#test"]}])

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[0]["user_posted"] == "alice"
        assert result[1]["id"] == "2"

    @patch("campaign_post_scraper.brightdata_client.httpx.Client")
    def test_execute_queries_deduplicates_by_id(self, mock_client_cls):
        """Posts with the same id across queries should be deduplicated."""
        posts_query1 = [
            {"id": "1", "user_posted": "alice", "description": "first"},
            {"id": "2", "user_posted": "bob", "description": "second"},
        ]
        posts_query2 = [
            {"id": "2", "user_posted": "bob", "description": "second"},
            {"id": "3", "user_posted": "carol", "description": "third"},
        ]
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = [
            _make_csv_response(posts_query1),
            _make_csv_response(posts_query2),
        ]
        mock_client_cls.return_value = mock_client

        client = BrightDataClient(api_key="key", base_url="http://api.test.com")
        result = client.execute_queries([{"q": "1"}, {"q": "2"}])

        assert len(result) == 3
        ids = [p["id"] for p in result]
        assert ids == ["1", "2", "3"]

    @patch("campaign_post_scraper.brightdata_client.httpx.Client")
    def test_execute_queries_raises_on_server_error(self, mock_client_cls):
        """A 500 error should raise an exception immediately."""
        error_response = httpx.Response(
            status_code=500,
            text="Internal Server Error",
            request=httpx.Request("POST", "http://api.test.com/search"),
        )
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = error_response
        mock_client_cls.return_value = mock_client

        client = BrightDataClient(api_key="key", base_url="http://api.test.com")

        with pytest.raises(httpx.HTTPStatusError):
            client.execute_queries([{"q": "test"}])

    @patch("campaign_post_scraper.brightdata_client.httpx.Client")
    def test_execute_queries_handles_rate_limit_429(self, mock_client_cls):
        """A 429 response should trigger rate limit pause and retry."""
        rate_limit_response = httpx.Response(
            status_code=429,
            text="",
            headers={"Retry-After": "1"},
            request=httpx.Request("POST", "http://api.test.com/search"),
        )
        success_response = _make_csv_response([{"id": "1", "user_posted": "alice", "description": "ok"}])

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = [rate_limit_response, success_response]
        mock_client_cls.return_value = mock_client

        client = BrightDataClient(api_key="key", base_url="http://api.test.com")

        with patch.object(client.rate_limiter, "on_rate_limit_signal") as mock_signal:
            with patch.object(client.rate_limiter, "acquire"):
                result = client.execute_queries([{"q": "test"}])

        assert len(result) == 1
        assert result[0]["id"] == "1"

    @patch("campaign_post_scraper.brightdata_client.httpx.Client")
    def test_execute_queries_empty_queries_returns_empty(self, mock_client_cls):
        """An empty query list should return an empty list."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        client = BrightDataClient(api_key="key", base_url="http://api.test.com")
        result = client.execute_queries([])

        assert result == []
        mock_client.post.assert_not_called()

    @patch("campaign_post_scraper.brightdata_client.httpx.Client")
    def test_execute_queries_calls_rate_limiter_acquire(self, mock_client_cls):
        """Each query should call rate_limiter.acquire() before sending."""
        posts = [{"id": "1", "user_posted": "alice", "description": "hi"}]
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = _make_csv_response(posts)
        mock_client_cls.return_value = mock_client

        client = BrightDataClient(api_key="key", base_url="http://api.test.com")

        with patch.object(client.rate_limiter, "acquire") as mock_acquire:
            client.execute_queries([{"q": "1"}, {"q": "2"}])

        # acquire should be called once per query
        assert mock_acquire.call_count == 2

    @patch("campaign_post_scraper.brightdata_client.httpx.Client")
    def test_execute_queries_sends_correct_headers(self, mock_client_cls):
        """Requests should include Authorization header with Bearer token."""
        posts = [{"id": "1", "user_posted": "alice", "description": "hi"}]
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = _make_csv_response(posts)
        mock_client_cls.return_value = mock_client

        client = BrightDataClient(api_key="my-secret-key", base_url="http://api.test.com")
        client.execute_queries([{"hashtags": ["#test"]}])

        call_kwargs = mock_client.post.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert headers["Authorization"] == "Bearer my-secret-key"

    @patch("campaign_post_scraper.brightdata_client.httpx.Client")
    def test_execute_queries_posts_to_search_endpoint(self, mock_client_cls):
        """Requests should POST to {base_url}/search."""
        posts = [{"id": "1", "user_posted": "alice", "description": "hi"}]
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = _make_csv_response(posts)
        mock_client_cls.return_value = mock_client

        client = BrightDataClient(api_key="key", base_url="http://api.test.com")
        client.execute_queries([{"hashtags": ["#test"]}])

        call_args = mock_client.post.call_args
        url = call_args.args[0] if call_args.args else call_args[0][0]
        assert url == "http://api.test.com/search"


class TestParseCsvResponse:
    """Tests for BrightDataClient._parse_csv_response()."""

    def test_parse_csv_response_basic(self):
        """Should parse CSV text into list of dicts."""
        csv_text = "id,user_posted,description\n1,alice,hello\n2,bob,world"
        client = BrightDataClient(api_key="key", base_url="http://test.com")
        result = client._parse_csv_response(csv_text)

        assert len(result) == 2
        assert result[0] == {"id": "1", "user_posted": "alice", "description": "hello"}
        assert result[1] == {"id": "2", "user_posted": "bob", "description": "world"}

    def test_parse_csv_response_empty(self):
        """Empty CSV text should return empty list."""
        client = BrightDataClient(api_key="key", base_url="http://test.com")
        result = client._parse_csv_response("")

        assert result == []

    def test_parse_csv_response_headers_only(self):
        """CSV with only headers should return empty list."""
        csv_text = "id,user_posted,description"
        client = BrightDataClient(api_key="key", base_url="http://test.com")
        result = client._parse_csv_response(csv_text)

        assert result == []
