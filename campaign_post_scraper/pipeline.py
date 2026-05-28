"""Pipeline orchestrator module for running the full scraping pipeline."""

from campaign_post_scraper.input_parser import parse_campaign_input
from campaign_post_scraper.query_constructor import build_queries
from campaign_post_scraper.brightdata_client import BrightDataClient
from campaign_post_scraper.post_mapper import map_posts
from campaign_post_scraper.json_exporter import export_json


def run_pipeline(
    input_csv_path: str,
    output_json_path: str,
    api_key: str,
    base_url: str,
) -> dict:
    """
    Runs the full pipeline:
    1. Parse input CSV
    2. Build queries
    3. Execute queries via BrightData (halt on error)
    4. Map posts to output schema
    5. Write JSON file

    Args:
        input_csv_path: Path to the campaign input CSV file.
        output_json_path: Path for the output JSON file.
        api_key: BrightData API key.
        base_url: BrightData API base URL.

    Returns:
        A dict with {"posts_collected": N, "output_path": output_json_path}

    Raises:
        Exception: On any stage failure with error details.
    """
    try:
        # Stage 1: Parse input CSV
        campaign_data = parse_campaign_input(input_csv_path)
    except Exception as e:
        raise RuntimeError(f"Stage 'input_parsing' failed: {e}") from e

    try:
        # Stage 2: Build queries
        queries = build_queries(
            hashtags=campaign_data["target_hashtags"],
            region=campaign_data["region"],
            seed_urls=campaign_data["approved_seed_urls"],
            start_date=campaign_data["start_date"],
            end_date=campaign_data["end_date"],
        )
    except Exception as e:
        raise RuntimeError(f"Stage 'query_construction' failed: {e}") from e

    try:
        # Stage 3: Execute queries via BrightData
        client = BrightDataClient(api_key=api_key, base_url=base_url)
        raw_posts = client.execute_queries(queries)
    except Exception as e:
        raise RuntimeError(f"Stage 'scraping' failed: {e}") from e

    try:
        # Stage 4: Map posts to output schema
        mapped_posts = map_posts(raw_posts)
    except Exception as e:
        raise RuntimeError(f"Stage 'post_mapping' failed: {e}") from e

    try:
        # Stage 5: Export to JSON
        export_result = export_json(mapped_posts, output_json_path)
    except Exception as e:
        raise RuntimeError(f"Stage 'json_export' failed: {e}") from e

    return {
        "posts_collected": export_result["posts_written"],
        "output_path": export_result["file_path"],
    }
