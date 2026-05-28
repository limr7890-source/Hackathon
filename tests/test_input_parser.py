"""Tests for the campaign input parser."""

import csv
import os
import tempfile

import pytest

from campaign_post_scraper.input_parser import parse_campaign_input


def _write_csv(rows: list[dict], path: str) -> None:
    """Helper to write a CSV file from a list of row dicts."""
    fieldnames = rows[0].keys()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class TestParseCampaignInput:
    """Unit tests for parse_campaign_input."""

    def test_single_hashtag_and_url(self, tmp_path):
        csv_file = tmp_path / "campaign.csv"
        _write_csv(
            [
                {
                    "Target_Hashtags": "#sale",
                    "Approved_Seed_URL": "https://x.com/post1",
                    "Region": "US",
                    "Start_Date": "2024-01-01",
                    "End_Date": "2024-03-01",
                }
            ],
            str(csv_file),
        )

        result = parse_campaign_input(str(csv_file))

        assert result["target_hashtags"] == ["#sale"]
        assert result["approved_seed_urls"] == ["https://x.com/post1"]
        assert result["region"] == "US"
        assert result["start_date"] == "2024-01-01"
        assert result["end_date"] == "2024-03-01"

    def test_multiple_hashtags_and_urls(self, tmp_path):
        csv_file = tmp_path / "campaign.csv"
        _write_csv(
            [
                {
                    "Target_Hashtags": "#sale, #discount, #promo",
                    "Approved_Seed_URL": "https://x.com/post1, https://x.com/post2",
                    "Region": "EU",
                    "Start_Date": "2024-06-01",
                    "End_Date": "2024-09-01",
                }
            ],
            str(csv_file),
        )

        result = parse_campaign_input(str(csv_file))

        assert result["target_hashtags"] == ["#sale", "#discount", "#promo"]
        assert result["approved_seed_urls"] == [
            "https://x.com/post1",
            "https://x.com/post2",
        ]
        assert result["region"] == "EU"
        assert result["start_date"] == "2024-06-01"
        assert result["end_date"] == "2024-09-01"

    def test_whitespace_is_stripped(self, tmp_path):
        csv_file = tmp_path / "campaign.csv"
        _write_csv(
            [
                {
                    "Target_Hashtags": "  #tag1 ,  #tag2  ",
                    "Approved_Seed_URL": " https://url1 , https://url2 ",
                    "Region": "  IL  ",
                    "Start_Date": " 2024-01-01 ",
                    "End_Date": " 2024-02-01 ",
                }
            ],
            str(csv_file),
        )

        result = parse_campaign_input(str(csv_file))

        assert result["target_hashtags"] == ["#tag1", "#tag2"]
        assert result["approved_seed_urls"] == ["https://url1", "https://url2"]
        assert result["region"] == "IL"
        assert result["start_date"] == "2024-01-01"
        assert result["end_date"] == "2024-02-01"

    def test_empty_values_are_excluded(self, tmp_path):
        csv_file = tmp_path / "campaign.csv"
        _write_csv(
            [
                {
                    "Target_Hashtags": "#tag1,,#tag2,",
                    "Approved_Seed_URL": "https://url1,,",
                    "Region": "US",
                    "Start_Date": "2024-01-01",
                    "End_Date": "2024-03-01",
                }
            ],
            str(csv_file),
        )

        result = parse_campaign_input(str(csv_file))

        assert result["target_hashtags"] == ["#tag1", "#tag2"]
        assert result["approved_seed_urls"] == ["https://url1"]
