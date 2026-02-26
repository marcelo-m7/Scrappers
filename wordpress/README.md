# WordPress Web Scraper

A Python web scraper that extracts content from websites using their sitemap.xml files.

## Features

- Fetches URLs from sitemap.xml
- Extracts title, paragraph content, and team information
- Removes unwanted elements (cookies notifications, footers)
- Saves data to JSON files with proper formatting
- Progress tracking for multiple URLs
- Automatic directory creation
- Robust error handling

## Installation

```bash
pip install -r requirements.txt
```

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML parsing for sitemaps

## Usage

### Basic Usage

```python
from main import web_scraper_start

# Use default settings (scrapes dspa.pt)
web_scraper_start()
```

### Custom Configuration

```python
from main import web_scraper_start

web_scraper_start(
    base_url='https://example.com/',
    sitemap_url='https://example.com/sitemap.xml',
    save_folder='output/scraped_data'
)
```

### Advanced Usage

```python
from main import WebScraper

# Create scraper instance
scraper = WebScraper(
    base_url='https://example.com/',
    sitemap_url='https://example.com/sitemap.xml',
    save_folder='output'
)

# Process entire site
scraper.process_site()

# Or process individual URLs
scraper.process_url('https://example.com/page')
```

## Output Format

Each URL is saved as a separate JSON file with the following structure:

```json
{
    "title": "Page Title",
    "content": "Extracted text content...",
    "metadata": {
        "url": "https://example.com/page"
    }
}
```

## File Naming

Files are named based on the URL structure:
- `domain_com_path_to_page.json`
- Special characters are replaced with underscores

## Error Handling

- Handles network errors gracefully
- Skips non-HTML content
- Creates output directories automatically
- Provides detailed error messages

## Notes

- The scraper respects standard HTTP headers (User-Agent)
- Only processes HTML content types
- Removes cookies notifications and footers automatically
- Extracts special team-container div content when present
