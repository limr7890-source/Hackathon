"""Campaign Post Scraper - A pipeline for collecting social media posts from X via BrightData."""

from campaign_post_scraper.input_parser import parse_campaign_input
from campaign_post_scraper.brightdata_client import BrightDataClient, RateLimiter
from campaign_post_scraper.post_mapper import map_posts
from campaign_post_scraper.json_exporter import export_json
from campaign_post_scraper.pipeline import run_pipeline

__all__ = [
    "parse_campaign_input",
    "BrightDataClient",
    "RateLimiter",
    "map_posts",
    "export_json",
    "run_pipeline",
]
