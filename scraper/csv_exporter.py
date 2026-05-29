"""CSV exporter module for writing mapped posts to a CSV file."""

import csv


def export_csv(data, output_path: str) -> dict:
    """
    Writes grouped post data to a CSV file.

    Each row has a 'target_hashtag' column indicating which group it belongs to.
    A post appearing under multiple hashtags will have multiple rows.

    Args:
        data: Dict mapping hashtag -> list of mapped post dicts.
        output_path: File path for the output CSV file.

    Returns:
        A dict with {"file_path": output_path, "posts_written": count}
    """
    fieldnames = [
        "target_hashtag", "post_id", "username", "hashtags",
        "timestamp", "content", "num_likes", "num_comments", "url", "score"
    ]

    count = 0
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for hashtag, posts in data.items():
            for post in posts:
                row = dict(post)
                row["target_hashtag"] = hashtag
                # Convert hashtags list to comma-separated string
                if isinstance(row.get("hashtags"), list):
                    row["hashtags"] = ", ".join(row["hashtags"])
                writer.writerow(row)
                count += 1

    return {"file_path": output_path, "posts_written": count}
