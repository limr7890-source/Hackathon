"""Input parser module for campaign CSV files."""

import csv


def parse_campaign_input(csv_path: str) -> dict:
    """
    Parses the campaign CSV and returns extracted campaign data.

    Args:
        csv_path: Path to the campaign input CSV file.

    Returns:
        A dict containing:
        {
            "post_urls": ["https://x.com/user/status/123", ...]
        }
    """
    post_urls = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("Approved_Seed_URL", "").strip()
            if url:
                post_urls.append(url)

    # Deduplicate while preserving order
    post_urls = list(dict.fromkeys(post_urls))

    return {
        "post_urls": post_urls,
    }
