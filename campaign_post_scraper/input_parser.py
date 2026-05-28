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
            "target_hashtags": ["#tag1", "#tag2", ...],
            "approved_seed_urls": ["url1", "url2", ...],
            "region": "US",
            "start_date": "2024-01-01",
            "end_date": "2024-03-01"
        }
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)

    target_hashtags = [
        tag.strip() for tag in row["Target_Hashtags"].split(",") if tag.strip()
    ]
    approved_seed_urls = [
        url.strip() for url in row["Approved_Seed_URL"].split(",") if url.strip()
    ]
    region = row["Region"].strip()
    start_date = row["Start_Date"].strip()
    end_date = row["End_Date"].strip()

    return {
        "target_hashtags": target_hashtags,
        "approved_seed_urls": approved_seed_urls,
        "region": region,
        "start_date": start_date,
        "end_date": end_date,
    }
