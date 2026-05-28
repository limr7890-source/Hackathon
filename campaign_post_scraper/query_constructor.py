"""Query constructor module for building BrightData search queries."""

from itertools import combinations


def build_queries(
    hashtags: list[str],
    region: str,
    seed_urls: list[str],
    start_date: str,
    end_date: str,
) -> list[dict]:
    """
    Builds BrightData queries from campaign data.

    Generates:
    - One query per hashtag × region combination (query_type: "hashtag_region")
    - One query per seed URL (query_type: "seed_url")
    - Subset queries for multi-hashtag combinations of size >= 2
      (query_type: "hashtag_region")

    Args:
        hashtags: List of target hashtags.
        region: Geographic region to scope the search.
        seed_urls: List of approved seed URLs.
        start_date: Campaign start date string.
        end_date: Campaign end date string.

    Returns:
        A list of query dicts to send to BrightData.
    """
    queries = []

    # One query per individual hashtag × region combination
    for hashtag in hashtags:
        queries.append({
            "hashtags": [hashtag],
            "region": region,
            "seed_urls": [],
            "start_date": start_date,
            "end_date": end_date,
            "query_type": "hashtag_region",
        })

    # One query per seed URL
    for url in seed_urls:
        queries.append({
            "hashtags": [],
            "region": region,
            "seed_urls": [url],
            "start_date": start_date,
            "end_date": end_date,
            "query_type": "seed_url",
        })

    # Subset queries for multi-hashtag combinations (size >= 2)
    for size in range(2, len(hashtags) + 1):
        for subset in combinations(hashtags, size):
            queries.append({
                "hashtags": list(subset),
                "region": region,
                "seed_urls": [],
                "start_date": start_date,
                "end_date": end_date,
                "query_type": "hashtag_region",
            })

    return queries
