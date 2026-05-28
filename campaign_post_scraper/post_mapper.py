"""Post mapper module for transforming BrightData rows to the output schema."""


def map_posts(raw_posts: list[dict]) -> list[dict]:
    """
    Maps BrightData CSV columns to the output schema.

    Mapping:
    - post_id <- id
    - username <- user_posted
    - hashtags <- hashtags
    - timestamp <- date_posted
    - content <- description
    - num_likes <- likes
    - num_comments <- replies
    - score <- 0 (default)

    Args:
        raw_posts: List of raw post dicts from BrightData.

    Returns:
        List of mapped post dicts conforming to the output schema.
    """
    return [
        {
            "post_id": post.get("id", ""),
            "username": post.get("user_posted", ""),
            "hashtags": post.get("hashtags", ""),
            "timestamp": post.get("date_posted", ""),
            "content": post.get("description", ""),
            "num_likes": int(post.get("likes", 0)),
            "num_comments": int(post.get("replies", 0)),
            "score": 0,
        }
        for post in raw_posts
    ]
