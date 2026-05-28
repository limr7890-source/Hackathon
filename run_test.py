"""
Test script for the Instagram Campaign Post Scraper pipeline.

Usage:
    python run_test.py                          # uses sample_campaign.csv
    python run_test.py path/to/your_file.csv    # uses a custom CSV
"""

import csv as csv_mod
import os
import sys

from campaign_post_scraper.pipeline import run_pipeline


def main():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        csv_path = sys.argv[1]
    else:
        csv_path = "sample_campaign.csv"

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        sys.exit(1)

    api_key = os.environ.get("BRIGHTDATA_API_KEY", "c755ca2c-f0c7-478d-bcb0-750606dda714")
    output_path = "output_posts.csv"
    seed_path = "seed_posts.csv"

    print(f"Input CSV:    {csv_path}")
    print(f"Seed CSV:     {seed_path}")
    print(f"Output CSV:   {output_path}")
    print(f"API Key:      {api_key[:8]}...{api_key[-4:]}")
    print("-" * 50)

    try:
        result = run_pipeline(
            input_csv_path=csv_path,
            output_csv_path=output_path,
            api_key=api_key,
            seed_csv_path=seed_path,
        )
    except RuntimeError as e:
        print(f"\nPIPELINE FAILED: {e}")
        sys.exit(1)

    print(f"\nPipeline completed successfully!")
    print(f"  Hashtags searched: {result['hashtag_count']}")
    print(f"  Total posts:       {result['total_posts']}")
    print(f"  Seed CSV:          {result['seed_path']}")
    print(f"  Output CSV:        {result['output_path']}")

    # Preview seed CSV
    if os.path.exists(seed_path):
        with open(seed_path, "r", encoding="utf-8") as f:
            rows = list(csv_mod.DictReader(f))
        print(f"\nSeed posts ({len(rows)} rows):")
        for row in rows[:3]:
            print(f"  {row.get('username', '')} - {row.get('url', '')}")

    # Preview output CSV
    if result["total_posts"] > 0:
        with open(output_path, "r", encoding="utf-8") as f:
            rows = list(csv_mod.DictReader(f))
        print(f"\nGrouped posts ({len(rows)} rows):")
        for row in rows[:5]:
            print(f"  [{row['target_hashtag']}] {row['username']} - {row['url']}")
    else:
        print("\nNo grouped posts were produced.")


if __name__ == "__main__":
    main()
