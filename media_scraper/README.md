# Odoo Media Scraper

A sitemap-first scraper that crawls a target website and downloads visual media assets focused on `.png` and `.svg` files.

## Module purpose

This module is designed for visual inspiration and reuse analysis workflows. It crawls website pages discovered from a sitemap and downloads useful visual assets such as:

- ERP mockups
- Product visuals
- UI illustrations
- Icons
- Other relevant graphics

The default configuration targets `https://www.odoo.com`.

## Directory structure

```text
media_scraper/
├── __init__.py
├── main.py                  # Core scraper + CLI entrypoint
├── README.md
├── requirements.txt
└── tests/
    └── test_media_scraper.py
```

## How sitemap discovery works

1. Start at `--sitemap` (default: `https://www.odoo.com/sitemap.xml`).
2. Parse XML.
3. If a sitemap index is found, recursively queue child sitemap URLs.
4. Collect page `<loc>` entries.
5. Keep only URLs belonging to the configured domain.
6. Remove URL query/fragment noise for cleaner deduplication.

## How media extraction works

For each page discovered from the sitemap:

1. Download and parse HTML.
2. Inspect common media-bearing tags (`img`, `source`, `link`, `meta`, `script`).
3. Parse attributes such as `src`, `srcset`, and `href`.
4. Resolve relative URLs to absolute URLs.
5. Filter only relevant `.png` / `.svg` candidates.
6. Download assets and classify into subfolders.

## Filtering rules

The scraper prioritizes assets containing include keywords in URL/context:

- `erp`, `mockup`, `product`, `ui`, `illustration`, `icon`, etc.

It also excludes likely-noise assets using skip keywords:

- `favicon`, `flag`, `payment`, `avatar`, `social`, etc.

Fallback behavior still accepts `.png` / `.svg` when path hints look visual (`image`, `icon`, `media`, `illustration`, `product`).

## Output layout

Assets are grouped by inferred category:

- `icons/`
- `images/`
- `mockups/`
- `illustrations/`
- `other/`

Filename format:

```text
{page-slug}__{asset-slug}__{content-hash8}.{ext}
```

This keeps filenames meaningful and idempotent while avoiding collisions.

## Running the scraper

Install dependencies:

```bash
cd media_scraper
pip install -r requirements.txt
```

Run with defaults (Odoo):

```bash
python main.py
```

Run with custom options:

```bash
python main.py \
  --domain https://www.odoo.com \
  --sitemap https://www.odoo.com/sitemap.xml \
  --output ./output/odoo_assets \
  --max-pages 80 \
  --max-assets 400 \
  --include-keyword onboarding \
  --skip-keyword partner
```

## Configuration options

- `--domain`: domain restriction for discovered pages.
- `--sitemap`: sitemap entrypoint URL.
- `--output`: output directory.
- `--max-pages`: crawl budget.
- `--max-assets`: download budget.
- `--timeout`: HTTP timeout.
- `--include-keyword`: add prioritization keywords.
- `--skip-keyword`: add exclusion keywords.
- `--log-level`: logging verbosity.

## Alignment with existing modules

- Follows the same Python + requests + BeautifulSoup stack used in `wordpress/`.
- Keeps a class-based scraper architecture with a convenience `main` runner.
- Expands the repository style by adding:
  - structured configuration (`dataclass`)
  - better URL/content deduplication
  - category-aware file output
  - CLI configurability for repeatable scraping runs

## Limitations and known edge cases

- Dynamic assets loaded only by JavaScript after render may be missed.
- Heuristic categorization may place some files in `other/`.
- Very strict filtering can skip useful assets if keywords are absent.
- Remote servers may throttle or block scraping activity.

## Example output structure

```text
output/odoo_assets/
├── icons/
│   ├── apps-inventory__warehouse-icon__ab12cd34.svg
├── images/
│   ├── apps-crm__pipeline-dashboard__67ef89aa.png
├── mockups/
│   ├── industries-retail__erp-screen__11bb22cc.png
├── illustrations/
│   ├── about__team-illustration__ffeedd00.svg
└── other/
    ├── home__promo-graphic__22334455.png
```
