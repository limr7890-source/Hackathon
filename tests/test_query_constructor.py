"""Tests for the query constructor module."""

import pytest

from campaign_post_scraper.query_constructor import build_queries


class TestBuildQueries:
    """Unit tests for build_queries."""

    def test_single_hashtag_produces_one_hashtag_region_query(self):
        queries = build_queries(
            hashtags=["#sale"],
            region="US",
            seed_urls=[],
            start_date="2024-01-01",
            end_date="2024-03-01",
        )

        hashtag_queries = [q for q in queries if q["query_type"] == "hashtag_region"]
        assert len(hashtag_queries) == 1
        assert hashtag_queries[0] == {
            "hashtags": ["#sale"],
            "region": "US",
            "seed_urls": [],
            "start_date": "2024-01-01",
            "end_date": "2024-03-01",
            "query_type": "hashtag_region",
        }

    def test_multiple_hashtags_produce_individual_queries(self):
        queries = build_queries(
            hashtags=["#sale", "#discount", "#promo"],
            region="EU",
            seed_urls=[],
            start_date="2024-06-01",
            end_date="2024-09-01",
        )

        individual = [q for q in queries if q["query_type"] == "hashtag_region" and len(q["hashtags"]) == 1]
        assert len(individual) == 3
        assert individual[0]["hashtags"] == ["#sale"]
        assert individual[1]["hashtags"] == ["#discount"]
        assert individual[2]["hashtags"] == ["#promo"]

    def test_seed_urls_produce_seed_url_queries(self):
        queries = build_queries(
            hashtags=[],
            region="US",
            seed_urls=["https://x.com/post1", "https://x.com/post2"],
            start_date="2024-01-01",
            end_date="2024-03-01",
        )

        seed_queries = [q for q in queries if q["query_type"] == "seed_url"]
        assert len(seed_queries) == 2
        assert seed_queries[0] == {
            "hashtags": [],
            "region": "US",
            "seed_urls": ["https://x.com/post1"],
            "start_date": "2024-01-01",
            "end_date": "2024-03-01",
            "query_type": "seed_url",
        }
        assert seed_queries[1]["seed_urls"] == ["https://x.com/post2"]

    def test_subset_queries_for_two_hashtags(self):
        queries = build_queries(
            hashtags=["#a", "#b"],
            region="US",
            seed_urls=[],
            start_date="2024-01-01",
            end_date="2024-03-01",
        )

        subset_queries = [q for q in queries if q["query_type"] == "hashtag_region" and len(q["hashtags"]) >= 2]
        # With 2 hashtags, only one subset of size 2: ["#a", "#b"]
        assert len(subset_queries) == 1
        assert subset_queries[0]["hashtags"] == ["#a", "#b"]

    def test_subset_queries_for_three_hashtags(self):
        queries = build_queries(
            hashtags=["#a", "#b", "#c"],
            region="US",
            seed_urls=[],
            start_date="2024-01-01",
            end_date="2024-03-01",
        )

        subset_queries = [q for q in queries if q["query_type"] == "hashtag_region" and len(q["hashtags"]) >= 2]
        # 3 subsets of size 2 + 1 subset of size 3 = 4
        assert len(subset_queries) == 4
        hashtag_sets = [q["hashtags"] for q in subset_queries]
        assert ["#a", "#b"] in hashtag_sets
        assert ["#a", "#c"] in hashtag_sets
        assert ["#b", "#c"] in hashtag_sets
        assert ["#a", "#b", "#c"] in hashtag_sets

    def test_all_queries_have_required_keys(self):
        queries = build_queries(
            hashtags=["#x", "#y"],
            region="IL",
            seed_urls=["https://example.com"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        required_keys = {"hashtags", "region", "seed_urls", "start_date", "end_date", "query_type"}
        for q in queries:
            assert set(q.keys()) == required_keys

    def test_empty_hashtags_and_urls_returns_empty(self):
        queries = build_queries(
            hashtags=[],
            region="US",
            seed_urls=[],
            start_date="2024-01-01",
            end_date="2024-03-01",
        )

        assert queries == []

    def test_combined_hashtags_and_seed_urls(self):
        queries = build_queries(
            hashtags=["#sale", "#promo"],
            region="US",
            seed_urls=["https://x.com/post1"],
            start_date="2024-01-01",
            end_date="2024-03-01",
        )

        hashtag_queries = [q for q in queries if q["query_type"] == "hashtag_region"]
        seed_queries = [q for q in queries if q["query_type"] == "seed_url"]

        # 2 individual + 1 subset of size 2 = 3 hashtag_region queries
        assert len(hashtag_queries) == 3
        # 1 seed URL query
        assert len(seed_queries) == 1
