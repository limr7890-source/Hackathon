"""Pipeline orchestrator module for running the full scraping pipeline."""

from campaign_post_scraper.input_parser import parse_campaign_input
from campaign_post_scraper.brightdata_client import BrightDataClient
from campaign_post_scraper.post_mapper import map_posts
from campaign_post_scraper.json_exporter import export_json


def run_pipeline(
    input_csv_path: str,
    output_json_path: str,
    api_key: str,
) -> dict:
    """
    Runs the full pipeline:
    1. Parse input CSV to extract post URLs
    2. Fetch posts from BrightData Dataset API
    3. Map posts to output schema
    4. Write JSON file

    Args:
        input_csv_path: Path to the campaign input CSV file.
        output_json_path: Path for the output JSON file.
        api_key: BrightData API key.

    Returns:
        A dict with {"posts_collected": N, "output_path": output_json_path}

    Raises:
        RuntimeError: On any stage failure with error details.
    """
    try:
        # Stage 1: Parse input CSV to get post URLs
        campaign_data = parse_campaign_input(input_csv_path)
    except Exception as e:
        raise RuntimeError(f"Stage 'input_parsing' failed: {e}") from e

    try:
        # Stage 2: Fetch posts from BrightData
        client = BrightDataClient(api_key=api_key)
        raw_posts = client.fetch_posts(campaign_data["post_urls"])
    except Exception as e:
        raise RuntimeError(f"Stage 'fetching' failed: {e}") from e

    try:
        # Stage 3: Map posts to output schema
        mapped_posts = map_posts(raw_posts)
    except Exception as e:
        raise RuntimeError(f"Stage 'post_mapping' failed: {e}") from e

    try:
        # Stage 4: Export to JSON
        export_result = export_json(mapped_posts, output_json_path)
    except Exception as e:
        raise RuntimeError(f"Stage 'json_export' failed: {e}") from e

    return {
        "posts_collected": export_result["posts_written"],
        "output_path": export_result["file_path"],
    }
