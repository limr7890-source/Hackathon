"""Campaign Post Scraper - A pipeline for collecting Instagram posts via BrightData."""

from scraper.input_parser import parse_campaign_input
from scraper.brightdata_client import BrightDataClient, RateLimiter
from scraper.post_mapper import map_posts
from scraper.json_exporter import export_json
from scraper.pipeline import run_pipeline

__all__ = [
    "parse_campaign_input",
    "BrightDataClient",
    "RateLimiter",
    "map_posts",
    "export_json",
    "run_pipeline",
]
