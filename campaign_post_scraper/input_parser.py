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
            "post_urls": ["https://instagram.com/p/...", ...],
            "target_hashtags": ["#dessert", "#food", ...]
        }
    """
    post_urls = []
    target_hashtags = []
    start_date = ""
    end_date = ""

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("Approved_Seed_URL", "").strip()
            if url:
                post_urls.append(url)

            hashtag = row.get("Target_Hashtag", "").strip()
            if hashtag:
                target_hashtags.append(hashtag)

            # Use dates from the row (last row wins if multiple)
            sd = row.get("Start_Date", "").strip()
            ed = row.get("End_Date", "").strip()
            if sd:
                start_date = sd
            if ed:
                end_date = ed

    # Deduplicate while preserving order
    post_urls = list(dict.fromkeys(post_urls))
    target_hashtags = list(dict.fromkeys(target_hashtags))

    return {
        "post_urls": post_urls,
        "target_hashtags": target_hashtags,
        "start_date": start_date,
        "end_date": end_date,
    }
