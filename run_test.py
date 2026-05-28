"""
Test script for the Campaign Post Scraper pipeline.

Usage:
    python run_test.py                          # uses sample_campaign.csv
    python run_test.py path/to/your_file.csv    # uses a custom CSV

Requires BRIGHTDATA_API_KEY environment variable to be set.
"""

import json
import os
import sys

from campaign_post_scraper.pipeline import run_pipeline


def main():
    # Determine input CSV path
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = "sample_campaign.csv"

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        sys.exit(1)

    # Get API key from environment
    api_key = "c755ca2c-f0c7-478d-bcb0-750606dda714"
    if not api_key:
        print("ERROR: Set the BRIGHTDATA_API_KEY environment variable.")
        print("  e.g.: set BRIGHTDATA_API_KEY=your-key-here")
        sys.exit(1)

    output_path = "output_posts.json"

    print(f"Input CSV:   {csv_path}")
    print(f"Output JSON: {output_path}")
    print(f"API Key:     {api_key[:8]}...{api_key[-4:]}")
    print("-" * 50)

    try:
        result = run_pipeline(
            input_csv_path=csv_path,
            output_json_path=output_path,
            api_key=api_key,
        )
    except RuntimeError as e:
        print(f"\nPIPELINE FAILED: {e}")
        sys.exit(1)

    print(f"\nPipeline completed successfully!")
    print(f"  Posts collected: {result['posts_collected']}")
    print(f"  Output file:    {result['output_path']}")

    # Print a preview of the output
    if result["posts_collected"] > 0:
        with open(output_path, "r", encoding="utf-8") as f:
            posts = json.load(f)

        print(f"\nFirst post preview:")
        first = posts[0]
        for key, value in first.items():
            display = str(value)[:80]
            print(f"  {key}: {display}")
    else:
        print("\nNo posts were collected.")


if __name__ == "__main__":
    main()
