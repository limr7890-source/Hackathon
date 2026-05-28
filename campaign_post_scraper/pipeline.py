"""Pipeline orchestrator module for the Instagram scraping pipeline."""

from campaign_post_scraper.input_parser import parse_campaign_input
from campaign_post_scraper.brightdata_client import BrightDataClient
from campaign_post_scraper.post_mapper import map_posts
from campaign_post_scraper.csv_exporter import export_csv


def run_pipeline(
    input_csv_path: str,
    output_csv_path: str,
    api_key: str,
    seed_csv_path: str = "seed_posts.csv",
) -> dict:
    """
    Runs the full pipeline:
    1. Parse CSV to get post URLs and target hashtags
    2. Fetch all posts by URL from BrightData → export as seed CSV
    3. Expand: group posts by target hashtag
    4. Map posts to output schema
    5. Export grouped CSV

    Args:
        input_csv_path: Path to the campaign input CSV.
        output_csv_path: Path for the grouped output CSV.
        api_key: BrightData API key.
        seed_csv_path: Path for the seed posts CSV (stage 1 results).

    Returns:
        Dict with hashtag_count, total_posts, output_path, seed_path.
    """
    try:
        campaign_data = parse_campaign_input(input_csv_path)
    except Exception as e:
        raise RuntimeError(f"Stage 'input_parsing' failed: {e}") from e

    target_hashtags = campaign_data.get("target_hashtags", [])
    post_urls = campaign_data.get("post_urls", [])

    if not post_urls:
        raise RuntimeError("No post URLs found in CSV")

    # Stage 1: Fetch all posts by URL
    try:
        client = BrightDataClient(api_key=api_key)
        print(f"Fetching {len(post_urls)} posts...")
        all_posts = client.fetch_posts(post_urls)
        print(f"  Fetched {len(all_posts)} posts")
    except Exception as e:
        raise RuntimeError(f"Stage 'fetching' failed: {e}") from e

    # Export seed posts CSV (stage 1 results)
    try:
        seed_mapped = map_posts(all_posts)
        seed_data = {"seed": seed_mapped}
        export_csv(seed_data, seed_csv_path)
        print(f"  Seed CSV written: {seed_csv_path}")
    except Exception as e:
        raise RuntimeError(f"Stage 'seed_export' failed: {e}") from e

    # Stage 2: Expand — group posts by target hashtag
    try:
        grouped_raw = client.expand_by_hashtags(all_posts, target_hashtags)
    except Exception as e:
        raise RuntimeError(f"Stage 'expansion' failed: {e}") from e

    # Stage 3: Map posts in each group to output schema
    try:
        grouped_mapped = {}
        for hashtag, posts in grouped_raw.items():
            grouped_mapped[hashtag] = map_posts(posts)
    except Exception as e:
        raise RuntimeError(f"Stage 'post_mapping' failed: {e}") from e

    # Stage 4: Export grouped CSV
    try:
        export_result = export_csv(grouped_mapped, output_csv_path)
    except Exception as e:
        raise RuntimeError(f"Stage 'csv_export' failed: {e}") from e

    total = sum(len(v) for v in grouped_mapped.values())
    return {
        "hashtag_count": len(grouped_mapped),
        "total_posts": total,
        "output_path": export_result["file_path"],
        "seed_path": seed_csv_path,
    }
