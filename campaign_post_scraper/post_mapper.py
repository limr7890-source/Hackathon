"""Post mapper module for transforming BrightData Instagram rows to the output schema."""


def map_posts(raw_posts: list[dict]) -> list[dict]:
    """
    Maps BrightData Instagram post fields to the output schema.

    Handles both "collect by URL" and "discover by URL" response formats:
    - collect: post_id, user_posted, hashtags (#prefixed), description, date_posted, likes, num_comments
    - discover: id, user_posted, post_hashtags (no #), caption, datetime, likes, comments

    Output schema:
    - post_id, username, hashtags, timestamp, content, num_likes, num_comments, url, score

    Args:
        raw_posts: List of raw post dicts from BrightData.

    Returns:
        List of mapped post dicts conforming to the output schema.
    """
    return [_map_single(post) for post in raw_posts]


def _map_single(post: dict) -> dict:
    """Map a single post dict to the output schema."""
    # ID: try post_id first (collect endpoint), then id (discover endpoint)
    post_id = post.get("post_id", "") or post.get("id", "") or post.get("pk", "")

    # Hashtags: collect uses "hashtags" with # prefix, discover uses "post_hashtags" without
    hashtags = post.get("hashtags") or post.get("post_hashtags") or []

    # Content: collect uses "description", discover uses "caption"
    content = post.get("description", "") or post.get("caption", "") or ""

    # Timestamp: collect uses "date_posted", discover uses "datetime"
    timestamp = post.get("date_posted", "") or post.get("datetime", "") or ""

    # Likes
    likes = post.get("likes", 0) or 0

    # Comments: collect uses "num_comments", discover uses "comments"
    comments = post.get("num_comments", 0) or post.get("comments", 0) or 0

    return {
        "post_id": str(post_id),
        "username": post.get("user_posted", ""),
        "hashtags": hashtags,
        "timestamp": timestamp,
        "content": content,
        "num_likes": int(likes),
        "num_comments": int(comments),
        "url": post.get("url", ""),
        "score": 0,
    }
