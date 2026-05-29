# Scraper Module API Documentation

## Overview

The scraper module is a modular, extensible system for fetching Instagram posts via the BrightData API. It supports fetching posts by URL, searching by user+hashtags, and searching by hashtags with date filtering.

---

## Architecture

```
scraper/
├── __init__.py              # Module exports
├── brightdata_client.py     # Core API client
├── input_parser.py          # CSV input parsing
├── post_mapper.py           # Data transformation
├── csv_exporter.py          # CSV output
├── json_exporter.py         # JSON output
├── pipeline.py              # Orchestration
└── query_constructor.py     # (Placeholder for future use)
```

### Design Principles
- **Modularity**: Each component has a single responsibility
- **Extensibility**: Easy to add new data sources or export formats
- **Error Handling**: Graceful degradation with warnings
- **Type Safety**: Full type hints for better IDE support
- **Rate Limiting**: Built-in throttling to respect API limits

---

## Core Components

### 1. BrightDataClient

**Location**: `scraper/brightdata_client.py`

The main client for interacting with the BrightData API.

#### Constructor

```python
BrightDataClient(
    api_key: str,
    dataset_id: str = "gd_lk5ns7kz21pck8jpis",
    rate_limit: int = 15,
    timeout: float = 120.0
)
```

**Parameters:**
- `api_key`: BrightData API key (required)
- `dataset_id`: Instagram dataset ID (default provided)
- `rate_limit`: Max requests per minute (default: 15)
- `timeout`: Request timeout in seconds (default: 120)

#### Methods

##### `fetch_posts(urls: List[str]) -> List[Dict]`

Fetch Instagram posts by direct URL.

**Parameters:**
- `urls`: List of Instagram post URLs

**Returns:**
- List of post dictionaries (deduplicated by post_id)

**Example:**
```python
client = BrightDataClient(api_key="your_key")
posts = client.fetch_posts([
    "https://www.instagram.com/p/DR_zZNFEjl7",
    "https://www.instagram.com/p/DSB_BoClXFT"
])
```

**Error Handling:**
- Prints warning for failed URLs
- Continues processing remaining URLs
- Returns empty list if all fail

---

##### `search_by_user_and_hashtags(username, hashtags, start_date, end_date) -> List[Dict]`

Search for posts from a specific user containing target hashtags within a date range.

**Parameters:**
- `username`: Instagram username (without @)
- `hashtags`: List of hashtags (with or without # prefix)
- `start_date`: Start date in DD.MM.YYYY format (optional)
- `end_date`: End date in DD.MM.YYYY format (optional)

**Returns:**
- List of matching posts

**Example:**
```python
posts = client.search_by_user_and_hashtags(
    username="cocacola",
    hashtags=["#FIFAWorldCup26", "#TrophyTour"],
    start_date="1.12.2025",
    end_date="1.4.2025"
)
```

**Use Case:**
- Expanding seed posts by finding more content from the same users

---

##### `search_by_hashtags(hashtags, start_date, end_date) -> Dict[str, List[Dict]]`

Search for all posts containing target hashtags within a date range.

**Parameters:**
- `hashtags`: List of hashtags to search (with or without # prefix)
- `start_date`: Start date in DD.MM.YYYY format (optional)
- `end_date`: End date in DD.MM.YYYY format (optional)

**Returns:**
- Dictionary mapping each hashtag to a list of posts

**Example:**
```python
grouped_posts = client.search_by_hashtags(
    hashtags=["#FIFAWorldCup26", "#CocaCola"],
    start_date="1.12.2025",
    end_date="1.4.2025"
)
# Returns: {"#FIFAWorldCup26": [...], "#CocaCola": [...]}
```

**Use Case:**
- Finding all campaign-related posts across Instagram

---

### 2. Input Parser

**Location**: `scraper/input_parser.py`

Parses campaign CSV files into structured data.

#### Function

```python
parse_campaign_input(csv_path: str) -> Dict
```

**Parameters:**
- `csv_path`: Path to campaign CSV file

**Returns:**
```python
{
    "post_urls": ["https://...", ...],
    "target_hashtags": ["#tag1", "#tag2", ...],
    "start_date": "1.12.2025",
    "end_date": "1.4.2025"
}
```

**Expected CSV Format:**
```csv
Target_Hashtags,Approved_Seed_URL,Region,Start_Date,End_Date
#TrophyTour,https://www.instagram.com/p/...,usa,1.12.2025,1.4.2025
```

**Features:**
- Deduplicates URLs and hashtags
- Handles both `Target_Hashtags` and `Target_Hashtag` columns
- Extracts dates from any row (last row wins)

---

### 3. Post Mapper

**Location**: `scraper/post_mapper.py`

Transforms raw BrightData responses into a standardized schema.

#### Function

```python
map_posts(raw_posts: List[Dict]) -> List[Dict]
```

**Input:** Raw BrightData post dictionaries

**Output Schema:**
```python
{
    "post_id": str,
    "username": str,
    "hashtags": List[str],
    "timestamp": str,
    "content": str,
    "num_likes": int,
    "num_comments": int,
    "url": str,
    "score": int  # Default: 0
}
```

**Handles Multiple Formats:**
- Collect endpoint: `post_id`, `user_posted`, `hashtags`, `description`, `date_posted`
- Discover endpoint: `id`, `user_posted`, `post_hashtags`, `caption`, `datetime`

---

### 4. CSV Exporter

**Location**: `scraper/csv_exporter.py`

Exports grouped posts to CSV format.

#### Function

```python
export_csv(data: Dict[str, List[Dict]], output_path: str) -> Dict
```

**Parameters:**
- `data`: Dictionary mapping hashtag → list of posts
- `output_path`: Output CSV file path

**Returns:**
```python
{
    "file_path": str,
    "posts_written": int
}
```

**Output Format:**
- Each row represents one post
- `target_hashtag` column indicates which group it belongs to
- Posts appearing under multiple hashtags have multiple rows

---

### 5. JSON Exporter

**Location**: `scraper/json_exporter.py`

Exports data to JSON format.

#### Function

```python
export_json(data: Union[List, Dict], output_path: str) -> Dict
```

**Parameters:**
- `data`: List of posts or dictionary grouped by hashtag
- `output_path`: Output JSON file path

**Returns:**
```python
{
    "file_path": str,
    "posts_written": int
}
```

---

### 6. Pipeline Orchestrator

**Location**: `scraper/pipeline.py`

High-level orchestration of the entire scraping workflow.

#### Function

```python
run_pipeline(
    input_csv_path: str,
    output_csv_path: str,
    api_key: str,
    seed_csv_path: str = "seed_posts.csv"
) -> Dict
```

**Parameters:**
- `input_csv_path`: Path to campaign input CSV
- `output_csv_path`: Path for hashtag search results
- `api_key`: BrightData API key
- `seed_csv_path`: Path for expanded seed posts

**Returns:**
```python
{
    "hashtag_count": int,
    "total_posts": int,
    "output_path": str,
    "seed_path": str
}
```

**Workflow:**

1. **Parse Input CSV**
   - Extract URLs, hashtags, dates

2. **Fetch Original Posts**
   - Fetch posts from provided URLs

3. **Expand Seed Posts**
   - Extract usernames from original posts
   - Search each user for more posts with target hashtags
   - Combine original + expanded → seed CSV

4. **Search by Hashtags**
   - Search Instagram for all posts with target hashtags
   - Filter by date range
   - Group by hashtag → output CSV

**Example:**
```python
from scraper.pipeline import run_pipeline

result = run_pipeline(
    input_csv_path="campaign_input.csv",
    output_csv_path="campaign_output.csv",
    api_key="your_api_key",
    seed_csv_path="seed_posts.csv"
)

print(f"Seed posts: {result['seed_path']}")
print(f"Campaign posts: {result['output_path']}")
print(f"Total posts: {result['total_posts']}")
```

---

## Rate Limiting

The `RateLimiter` class automatically throttles requests:

- **Default**: 15 requests per minute
- **Sliding window**: Tracks requests over 60-second window
- **Auto-retry**: Handles 429 responses with `Retry-After` header
- **Configurable**: Adjust via `rate_limit` parameter

---

## Error Handling Strategy

### Graceful Degradation
- Individual URL failures don't stop the pipeline
- Warnings printed to console
- Empty results returned for failed operations

### Exception Types
- `RuntimeError`: API errors (4xx, 5xx responses)
- Prints warnings for non-critical failures
- Continues processing remaining items

---

## Extensibility Points

### Adding New Data Sources

1. Create a new client class (e.g., `TwitterClient`)
2. Implement the same interface:
   - `fetch_posts(urls)`
   - `search_by_user_and_hashtags(...)`
   - `search_by_hashtags(...)`
3. Update pipeline to use new client

### Adding New Export Formats

1. Create new exporter (e.g., `parquet_exporter.py`)
2. Implement `export_<format>(data, output_path) -> dict`
3. Import in pipeline and call as needed

### Custom Post Processing

Extend `post_mapper.py` to add custom fields:

```python
def _map_single(post: dict) -> dict:
    mapped = {
        # ... existing fields ...
        "custom_field": compute_custom_value(post)
    }
    return mapped
```

---

## Testing Recommendations

### Unit Tests
```python
# Test individual components
def test_parse_campaign_input():
    result = parse_campaign_input("test_input.csv")
    assert "post_urls" in result
    assert "target_hashtags" in result

def test_map_posts():
    raw = [{"post_id": "123", "user_posted": "test"}]
    mapped = map_posts(raw)
    assert mapped[0]["post_id"] == "123"
```

### Integration Tests
```python
# Test full pipeline with mock API
def test_pipeline_end_to_end():
    with mock_brightdata_api():
        result = run_pipeline(...)
        assert result["total_posts"] > 0
```

---

## Performance Considerations

### Rate Limiting
- Default: 15 req/min = ~900 req/hour
- For 100 URLs: ~7 minutes
- For 10 hashtags: ~1 minute

### Optimization Tips
1. **Batch URLs**: Group related URLs together
2. **Cache Results**: Store intermediate results
3. **Parallel Processing**: Use async for independent requests (future enhancement)
4. **Increase Rate Limit**: If API plan allows

---

## Future Enhancements

### Planned Features
- [ ] Async/await support for parallel requests
- [ ] Caching layer for repeated queries
- [ ] Retry logic with exponential backoff
- [ ] Progress bars for long-running operations
- [ ] Pagination support for large result sets
- [ ] Custom filters (engagement thresholds, verified users, etc.)

### Potential Integrations
- [ ] Database storage (PostgreSQL, MongoDB)
- [ ] Cloud storage (S3, GCS)
- [ ] Real-time streaming
- [ ] Webhook notifications

---

## Summary

### ✅ Strengths
- **Modular**: Each component is independent and testable
- **Extensible**: Easy to add new features or data sources
- **Robust**: Graceful error handling and rate limiting
- **Well-Documented**: Type hints and docstrings throughout
- **Production-Ready**: Handles edge cases and API limits

### 🎯 Use Cases
1. **Campaign Monitoring**: Track brand mentions and hashtags
2. **Influencer Discovery**: Find users posting about topics
3. **Competitive Analysis**: Monitor competitor campaigns
4. **Content Research**: Discover trending posts and hashtags
5. **Training Data Collection**: Build datasets for ML models

---

## Quick Start

```python
# 1. Import the pipeline
from scraper.pipeline import run_pipeline

# 2. Run the full workflow
result = run_pipeline(
    input_csv_path="campaign_input.csv",
    output_csv_path="campaign_output.csv",
    api_key="your_brightdata_api_key"
)

# 3. Access results
print(f"✅ Seed posts: {result['seed_path']}")
print(f"✅ Campaign posts: {result['output_path']}")
print(f"📊 Total posts collected: {result['total_posts']}")
```

---

## Support

For issues or questions:
1. Check error messages in console output
2. Verify API key and rate limits
3. Ensure CSV format matches expected schema
4. Review BrightData API documentation

---

**Version**: 1.0  
**Last Updated**: 2026-05-29  
**Maintainer**: Hackathon Team
