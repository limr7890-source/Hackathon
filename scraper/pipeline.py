"""Pipeline orchestrator module for the Instagram scraping pipeline."""

from scraper.input_parser import parse_campaign_input
from scraper.brightdata_client import BrightDataClient
from scraper.post_mapper import map_posts
from scraper.csv_exporter import export_csv


def run_pipeline(
    input_csv_path: str,
    output_csv_path: str,
    api_key: str,
    seed_csv_path: str = "seed_posts.csv",
) -> dict:
    """
    Runs the full pipeline:
    1. Parse CSV to get post URLs, target hashtags, and date range
    2. Fetch original posts by URL from BrightData
    3. For each original post, search for more posts from the same user with target hashtags → seed CSV
    4. Search for all posts with target hashtags (any user) → output CSV

    Args:
        input_csv_path: Path to the campaign input CSV.
        output_csv_path: Path for the grouped output CSV.
        api_key: BrightData API key.
        seed_csv_path: Path for the seed posts CSV (expanded results from seed users).

    Returns:
        Dict with hashtag_count, total_posts, output_path, seed_path.
    """
    # Stage 1: Parse input CSV
    try:
        campaign_data = parse_campaign_input(input_csv_path)
    except Exception as e:
        raise RuntimeError(f"Stage 'input_parsing' failed: {e}") from e

    target_hashtags = campaign_data.get("target_hashtags", [])
    post_urls = campaign_data.get("post_urls", [])
    start_date = campaign_data.get("start_date", "")
    end_date = campaign_data.get("end_date", "")

    if not post_urls:
        raise RuntimeError("No post URLs found in CSV")

    client = BrightDataClient(api_key=api_key)

    # Stage 2: Fetch original posts by URL
    try:
        print(f"Fetching {len(post_urls)} original posts...")
        original_posts = client.fetch_posts(post_urls)
        print(f"  Fetched {len(original_posts)} original posts")
    except Exception as e:
        raise RuntimeError(f"Stage 'fetching_original_posts' failed: {e}") from e

    # Stage 3: Expand seed posts - search for more posts from the same users
    try:
        print(f"Expanding seed posts by searching user posts with target hashtags...")
        all_seed_posts = list(original_posts)  # Start with original posts
        seen_post_ids = {p.get("post_id") or p.get("id") or p.get("pk") for p in original_posts}
        
        # Extract unique usernames from original posts
        usernames = {post.get("user_posted", "").strip() for post in original_posts}
        usernames = {u for u in usernames if u}  # Remove empty strings
        
        print(f"  Found {len(usernames)} unique users from original posts")
        
        # For each user, search for their posts with target hashtags
        for username in usernames:
            print(f"  Searching posts from @{username}...")
            user_posts = client.search_by_user_and_hashtags(
                username=username,
                hashtags=target_hashtags,
                start_date=start_date,
                end_date=end_date
            )
            
            # Add new posts (avoid duplicates)
            for post in user_posts:
                post_id = post.get("post_id") or post.get("id") or post.get("pk")
                if post_id and post_id not in seen_post_ids:
                    seen_post_ids.add(post_id)
                    all_seed_posts.append(post)
        
        print(f"  Total seed posts after expansion: {len(all_seed_posts)}")
        
        # Export expanded seed posts CSV
        seed_mapped = map_posts(all_seed_posts)
        seed_data = {"seed": seed_mapped}
        export_csv(seed_data, seed_csv_path)
        print(f"  Seed CSV written: {seed_csv_path}")
    except Exception as e:
        raise RuntimeError(f"Stage 'seed_expansion' failed: {e}") from e

    # Stage 4: Search for all posts with target hashtags (any user)
    try:
        print(f"Searching for all posts with target hashtags...")
        grouped_raw = client.search_by_hashtags(
            hashtags=target_hashtags,
            start_date=start_date,
            end_date=end_date
        )
        print(f"  Found posts for {len(grouped_raw)} hashtags")
    except Exception as e:
        raise RuntimeError(f"Stage 'hashtag_search' failed: {e}") from e

    # Stage 5: Map posts in each group to output schema
    try:
        grouped_mapped = {}
        for hashtag, posts in grouped_raw.items():
            grouped_mapped[hashtag] = map_posts(posts)
            print(f"  {hashtag}: {len(posts)} posts")
    except Exception as e:
        raise RuntimeError(f"Stage 'post_mapping' failed: {e}") from e

    # Stage 6: Export grouped CSV
    try:
        export_result = export_csv(grouped_mapped, output_csv_path)
        print(f"  Output CSV written: {output_csv_path}")
    except Exception as e:
        raise RuntimeError(f"Stage 'csv_export' failed: {e}") from e

    total = sum(len(v) for v in grouped_mapped.values())
    return {
        "hashtag_count": len(grouped_mapped),
        "total_posts": total,
        "output_path": export_result["file_path"],
        "seed_path": seed_csv_path,
    }
