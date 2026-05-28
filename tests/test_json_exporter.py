"""Tests for the JSON exporter module."""

import json
import os
import tempfile

import pytest

from campaign_post_scraper.json_exporter import export_json


class TestExportJson:
    """Unit tests for export_json function."""

    def test_writes_posts_to_json_file(self, tmp_path):
        """Test that posts are written as a JSON list to the specified file."""
        posts = [
            {"post_id": "1", "username": "alice", "hashtags": "#test", "timestamp": "2024-01-01", "content": "Hello", "num_likes": 10, "num_comments": 2, "score": 0},
            {"post_id": "2", "username": "bob", "hashtags": "#demo", "timestamp": "2024-01-02", "content": "World", "num_likes": 5, "num_comments": 1, "score": 0},
        ]
        output_path = str(tmp_path / "output.json")

        result = export_json(posts, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            written_data = json.load(f)

        assert written_data == posts

    def test_returns_file_path_and_posts_written(self, tmp_path):
        """Test that the return dict contains file_path and posts_written."""
        posts = [
            {"post_id": "1", "username": "alice", "hashtags": "#test", "timestamp": "2024-01-01", "content": "Hello", "num_likes": 10, "num_comments": 2, "score": 0},
        ]
        output_path = str(tmp_path / "output.json")

        result = export_json(posts, output_path)

        assert result == {"file_path": output_path, "posts_written": 1}

    def test_empty_list_writes_empty_json_array(self, tmp_path):
        """Test that an empty list writes an empty JSON array."""
        output_path = str(tmp_path / "empty.json")

        result = export_json([], output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            written_data = json.load(f)

        assert written_data == []
        assert result == {"file_path": output_path, "posts_written": 0}

    def test_handles_unicode_content(self, tmp_path):
        """Test that unicode characters are preserved (ensure_ascii=False)."""
        posts = [
            {"post_id": "1", "username": "用户", "hashtags": "#テスト", "timestamp": "2024-01-01", "content": "Héllo wörld 🌍", "num_likes": 0, "num_comments": 0, "score": 0},
        ]
        output_path = str(tmp_path / "unicode.json")

        export_json(posts, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            written_data = json.load(f)

        assert written_data[0]["username"] == "用户"
        assert written_data[0]["hashtags"] == "#テスト"
        assert written_data[0]["content"] == "Héllo wörld 🌍"

    def test_json_is_formatted_with_indent(self, tmp_path):
        """Test that the JSON output is human-readable with indentation."""
        posts = [{"post_id": "1", "username": "alice", "hashtags": "#test", "timestamp": "2024-01-01", "content": "Hello", "num_likes": 10, "num_comments": 2, "score": 0}]
        output_path = str(tmp_path / "formatted.json")

        export_json(posts, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()

        # indent=2 means the JSON should have newlines and spaces
        assert "\n" in content
        assert "  " in content
