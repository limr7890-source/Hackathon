"""Tests for the RateLimiter class."""

import time
from unittest.mock import patch

import pytest

from campaign_post_scraper.brightdata_client import RateLimiter


class TestRateLimiterAcquire:
    """Unit tests for RateLimiter.acquire()."""

    def test_acquire_allows_requests_under_limit(self):
        """Requests under the limit should proceed immediately."""
        limiter = RateLimiter(max_requests_per_minute=5)

        start = time.time()
        for _ in range(5):
            limiter.acquire()
        elapsed = time.time() - start

        # All 5 requests should complete nearly instantly
        assert elapsed < 0.1

    def test_acquire_blocks_when_at_capacity(self):
        """When at capacity, acquire should block until a slot opens."""
        limiter = RateLimiter(max_requests_per_minute=2)

        # Fill up the window
        limiter.acquire()
        limiter.acquire()

        # Manually backdate the oldest timestamp so it expires quickly
        limiter._request_timestamps[0] = time.time() - 59.5

        start = time.time()
        limiter.acquire()
        elapsed = time.time() - start

        # Should have waited ~0.5 seconds for the oldest to expire
        assert elapsed < 1.0

    def test_acquire_tracks_timestamps(self):
        """Each acquire call should record a timestamp."""
        limiter = RateLimiter(max_requests_per_minute=10)

        limiter.acquire()
        limiter.acquire()
        limiter.acquire()

        assert len(limiter._request_timestamps) == 3

    def test_acquire_removes_expired_timestamps(self):
        """Timestamps older than 60 seconds should be pruned."""
        limiter = RateLimiter(max_requests_per_minute=2)

        # Simulate an old request from 61 seconds ago
        limiter._request_timestamps = [time.time() - 61]

        limiter.acquire()

        # Old timestamp should be pruned, only the new one remains
        assert len(limiter._request_timestamps) == 1


class TestRateLimiterOnRateLimitSignal:
    """Unit tests for RateLimiter.on_rate_limit_signal()."""

    @patch("campaign_post_scraper.brightdata_client.time.sleep")
    def test_on_rate_limit_signal_sleeps_for_reset_time(self, mock_sleep):
        """Should sleep for the specified reset_time."""
        limiter = RateLimiter()

        limiter.on_rate_limit_signal(5.0)

        mock_sleep.assert_called_once_with(5.0)

    @patch("campaign_post_scraper.brightdata_client.time.sleep")
    def test_on_rate_limit_signal_zero_does_not_sleep(self, mock_sleep):
        """A reset_time of 0 should not trigger a sleep."""
        limiter = RateLimiter()

        limiter.on_rate_limit_signal(0.0)

        mock_sleep.assert_not_called()

    @patch("campaign_post_scraper.brightdata_client.time.sleep")
    def test_on_rate_limit_signal_negative_does_not_sleep(self, mock_sleep):
        """A negative reset_time should not trigger a sleep."""
        limiter = RateLimiter()

        limiter.on_rate_limit_signal(-1.0)

        mock_sleep.assert_not_called()
