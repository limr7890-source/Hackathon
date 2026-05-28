"""Tests for the post_mapper module."""

from campaign_post_scraper.post_mapper import map_posts


def test_map_posts_basic():
    """Test basic column mapping from BrightData format to output schema."""
    raw_posts = [
        {
            "id": "123456",
            "user_posted": "alice",
            "hashtags": "#python #coding",
            "date_posted": "2024-01-15T10:30:00Z",
            "description": "Hello world!",
            "likes": "42",
            "replies": "7",
        }
    ]
    result = map_posts(raw_posts)
    assert len(result) == 1
    post = result[0]
    assert post["post_id"] == "123456"
    assert post["username"] == "alice"
    assert post["hashtags"] == "#python #coding"
    assert post["timestamp"] == "2024-01-15T10:30:00Z"
    assert post["content"] == "Hello world!"
    assert post["num_likes"] == 42
    assert post["num_comments"] == 7
    assert post["score"] == 0


def test_map_posts_score_always_zero():
    """Test that score is always set to 0 regardless of input."""
    raw_posts = [
        {"id": "1", "user_posted": "u", "hashtags": "", "date_posted": "", "description": "", "likes": "0", "replies": "0"},
        {"id": "2", "user_posted": "v", "hashtags": "", "date_posted": "", "description": "", "likes": "100", "replies": "50"},
    ]
    result = map_posts(raw_posts)
    for post in result:
        assert post["score"] == 0


def test_map_posts_empty_list():
    """Test that an empty input returns an empty output."""
    assert map_posts([]) == []


def test_map_posts_numeric_conversion():
    """Test that likes and replies are converted to int even when given as strings."""
    raw_posts = [
        {
            "id": "789",
            "user_posted": "bob",
            "hashtags": "#test",
            "date_posted": "2024-02-01",
            "description": "Testing",
            "likes": "1000",
            "replies": "55",
        }
    ]
    result = map_posts(raw_posts)
    assert result[0]["num_likes"] == 1000
    assert result[0]["num_comments"] == 55
    assert isinstance(result[0]["num_likes"], int)
    assert isinstance(result[0]["num_comments"], int)


def test_map_posts_missing_fields_use_defaults():
    """Test that missing fields default to empty string or 0."""
    raw_posts = [{}]
    result = map_posts(raw_posts)
    assert len(result) == 1
    post = result[0]
    assert post["post_id"] == ""
    assert post["username"] == ""
    assert post["hashtags"] == ""
    assert post["timestamp"] == ""
    assert post["content"] == ""
    assert post["num_likes"] == 0
    assert post["num_comments"] == 0
    assert post["score"] == 0


def test_map_posts_multiple_posts():
    """Test mapping multiple posts at once."""
    raw_posts = [
        {"id": "a1", "user_posted": "user1", "hashtags": "#h1", "date_posted": "2024-01-01", "description": "Post 1", "likes": "10", "replies": "2"},
        {"id": "a2", "user_posted": "user2", "hashtags": "#h2", "date_posted": "2024-01-02", "description": "Post 2", "likes": "20", "replies": "4"},
        {"id": "a3", "user_posted": "user3", "hashtags": "#h3", "date_posted": "2024-01-03", "description": "Post 3", "likes": "30", "replies": "6"},
    ]
    result = map_posts(raw_posts)
    assert len(result) == 3
    assert result[0]["post_id"] == "a1"
    assert result[1]["post_id"] == "a2"
    assert result[2]["post_id"] == "a3"
