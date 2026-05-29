"""JSON exporter module for writing mapped posts to a JSON file."""

import json


def export_json(data, output_path: str) -> dict:
    """
    Writes data to a JSON file.

    Args:
        data: Either a list of post dicts or a dict grouped by hashtag.
        output_path: File path for the output JSON file.

    Returns:
        A dict with {"file_path": output_path, "posts_written": count}
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Count posts
    if isinstance(data, list):
        count = len(data)
    elif isinstance(data, dict):
        count = sum(len(v) for v in data.values() if isinstance(v, list))
    else:
        count = 0

    return {"file_path": output_path, "posts_written": count}
