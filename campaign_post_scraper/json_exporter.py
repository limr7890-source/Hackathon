"""JSON exporter module for writing mapped posts to a JSON file."""

import json


def export_json(posts: list[dict], output_path: str) -> dict:
    """
    Writes posts to a JSON file.

    Args:
        posts: List of mapped post dicts to export.
        output_path: File path for the output JSON file.

    Returns:
        A dict with {"file_path": output_path, "posts_written": len(posts)}
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    return {"file_path": output_path, "posts_written": len(posts)}
