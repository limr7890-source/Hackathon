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
    target_hashtags = []
    approved_seed_urls = []
    region = ""
    start_date = ""
    end_date = ""

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Accumulate hashtags and URLs from all rows
            target_hashtags.extend(
                tag.strip() for tag in row["Target_Hashtags"].split(",") if tag.strip()
            )
            approved_seed_urls.extend(
                url.strip() for url in row["Approved_Seed_URL"].split(",") if url.strip()
            )
            # Use the last row's region/dates (or override per your logic)
            region = row["Region"].strip()
            start_date = row["Start_Date"].strip()
            end_date = row["End_Date"].strip()

    # Deduplicate while preserving order
    target_hashtags = list(dict.fromkeys(target_hashtags))
    approved_seed_urls = list(dict.fromkeys(approved_seed_urls))

    return {
        "target_hashtags": target_hashtags,
        "approved_seed_urls": approved_seed_urls,
        "region": region,
        "start_date": start_date,
        "end_date": end_date,
    }
