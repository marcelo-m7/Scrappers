import argparse
import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup


@dataclass
class MediaScraperConfig:
    domain: str = "https://www.odoo.com"
    sitemap_url: str = "https://www.odoo.com/sitemap.xml"
    output_dir: str = "media_scraper_output"
    timeout: int = 20
    max_pages: Optional[int] = 60
    max_assets: Optional[int] = 300
    include_extensions: Set[str] = field(default_factory=lambda: {".png", ".svg"})
    include_keywords: Set[str] = field(
        default_factory=lambda: {
            "erp",
            "mockup",
            "product",
            "ui",
            "illustration",
            "icon",
            "dashboard",
            "app",
            "software",
            "screen",
            "interface",
            "workflow",
        }
    )
    skip_keywords: Set[str] = field(
        default_factory=lambda: {
            "favicon",
            "flag",
            "payment",
            "partner",
            "avatar",
            "social",
            "cookie",
            "tracker",
        }
    )


class SiteMediaScraper:
    def __init__(self, config: MediaScraperConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; SiteMediaScraper/1.0)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        self.output_dir = Path(config.output_dir)
        self.seen_asset_urls: Set[str] = set()
        self.seen_content_hashes: Set[str] = set()
        self.downloaded_assets: List[Path] = []

    def run(self) -> Dict[str, int]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        page_urls = self.fetch_sitemap_urls(self.config.sitemap_url)
        if self.config.max_pages:
            page_urls = page_urls[: self.config.max_pages]

        logging.info("Discovered %s pages from sitemap.", len(page_urls))
        for index, page_url in enumerate(page_urls, 1):
            if self.config.max_assets and len(self.downloaded_assets) >= self.config.max_assets:
                logging.info("Reached max_assets=%s. Stopping crawl.", self.config.max_assets)
                break
            logging.info("[%s/%s] Crawling %s", index, len(page_urls), page_url)
            self.scrape_page_assets(page_url)

        return {
            "pages_discovered": len(page_urls),
            "assets_downloaded": len(self.downloaded_assets),
            "assets_seen": len(self.seen_asset_urls),
        }

    def fetch_sitemap_urls(self, sitemap_url: str) -> List[str]:
        urls: List[str] = []
        visited_sitemaps: Set[str] = set()
        queue = [sitemap_url]

        while queue:
            current = queue.pop(0)
            if current in visited_sitemaps:
                continue
            visited_sitemaps.add(current)

            try:
                response = self.session.get(current, timeout=self.config.timeout)
                response.raise_for_status()
            except requests.RequestException as exc:
                logging.warning("Unable to fetch sitemap %s: %s", current, exc)
                continue

            soup = BeautifulSoup(response.content, "xml")
            sitemap_entries = [loc.get_text(strip=True) for loc in soup.find_all("sitemap") for loc in loc.find_all("loc")]
            if sitemap_entries:
                queue.extend(sitemap_entries)
                continue

            page_entries = [loc.get_text(strip=True) for loc in soup.find_all("loc")]
            for url in page_entries:
                normalized = self.normalize_page_url(url)
                if self.is_valid_page_url(normalized):
                    urls.append(normalized)

        return list(dict.fromkeys(urls))

    def normalize_page_url(self, url: str) -> str:
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))

    def is_valid_page_url(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = urlparse(self.config.domain).netloc
        if parsed.netloc != domain:
            return False
        return not parsed.path.endswith(".xml")

    def scrape_page_assets(self, page_url: str) -> None:
        try:
            response = self.session.get(page_url, timeout=self.config.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            logging.warning("Unable to fetch page %s: %s", page_url, exc)
            return

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return

        soup = BeautifulSoup(response.text, "html.parser")
        candidates = self.extract_media_candidates(soup, page_url)
        for asset in candidates:
            if self.config.max_assets and len(self.downloaded_assets) >= self.config.max_assets:
                break
            self.download_asset(asset)

    def extract_media_candidates(self, soup: BeautifulSoup, page_url: str) -> List[Dict[str, str]]:
        candidates: List[Dict[str, str]] = []
        attr_map = {
            "img": ["src", "data-src", "data-original", "srcset"],
            "source": ["src", "srcset"],
            "link": ["href"],
            "meta": ["content"],
            "script": ["src"],
        }

        for tag_name, attrs in attr_map.items():
            for node in soup.find_all(tag_name):
                context = " ".join(
                    filter(
                        None,
                        [
                            node.get("alt"),
                            node.get("title"),
                            node.get("class") and " ".join(node.get("class")),
                            page_url,
                        ],
                    )
                ).lower()
                for attr in attrs:
                    raw_value = node.get(attr)
                    if not raw_value:
                        continue
                    for media_url in self.expand_candidate_urls(raw_value, page_url):
                        if self.should_keep_asset(media_url, context):
                            candidates.append({"url": media_url, "page_url": page_url, "context": context})

        deduped = {item["url"]: item for item in candidates}
        return list(deduped.values())

    def expand_candidate_urls(self, raw_value: str, page_url: str) -> Iterable[str]:
        parts = [p.strip() for p in raw_value.split(",") if p.strip()]
        for part in parts:
            url_part = part.split(" ")[0]
            joined = urljoin(page_url, url_part)
            parsed = urlparse(joined)
            if parsed.scheme in {"http", "https"}:
                yield urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))

    def should_keep_asset(self, asset_url: str, context: str) -> bool:
        parsed = urlparse(asset_url)
        extension = Path(parsed.path).suffix.lower()
        if extension not in self.config.include_extensions:
            return False

        combined = f"{asset_url.lower()} {context}"
        if any(skip in combined for skip in self.config.skip_keywords):
            return False

        if any(keyword in combined for keyword in self.config.include_keywords):
            return True

        # fallback rule: keep png/svg under media-like paths
        return any(token in parsed.path.lower() for token in ["image", "icon", "media", "illustration", "product"])

    def download_asset(self, asset: Dict[str, str]) -> None:
        asset_url = asset["url"]
        if asset_url in self.seen_asset_urls:
            return
        self.seen_asset_urls.add(asset_url)

        try:
            response = self.session.get(asset_url, timeout=self.config.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            logging.warning("Failed downloading %s: %s", asset_url, exc)
            return

        extension = Path(urlparse(asset_url).path).suffix.lower()
        if extension not in self.config.include_extensions:
            return

        content_hash = hashlib.sha256(response.content).hexdigest()
        if content_hash in self.seen_content_hashes:
            return

        self.seen_content_hashes.add(content_hash)
        category = self.pick_category(asset_url, asset["context"])
        category_dir = self.output_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        filename = self.build_filename(asset_url, asset["page_url"], extension, content_hash)
        path = category_dir / filename
        if path.exists():
            return

        path.write_bytes(response.content)
        self.downloaded_assets.append(path)
        logging.info("Saved %s", path)

    def pick_category(self, asset_url: str, context: str) -> str:
        text = f"{asset_url.lower()} {context}"
        if "icon" in text:
            return "icons"
        if "mockup" in text or "erp" in text or "screen" in text:
            return "mockups"
        if "illustration" in text:
            return "illustrations"
        if "product" in text or "ui" in text or "dashboard" in text:
            return "images"
        return "other"

    def build_filename(self, asset_url: str, page_url: str, extension: str, content_hash: str) -> str:
        page_slug = self.slugify(urlparse(page_url).path.strip("/") or "home")
        asset_slug = self.slugify(Path(urlparse(asset_url).path).stem)
        short_hash = content_hash[:8]
        return f"{page_slug}__{asset_slug}__{short_hash}{extension}"

    @staticmethod
    def slugify(value: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
        return cleaned[:80] if cleaned else "asset"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sitemap-driven website media scraper")
    parser.add_argument("--domain", default="https://www.odoo.com", help="Target domain")
    parser.add_argument("--sitemap", default="https://www.odoo.com/sitemap.xml", help="Sitemap URL")
    parser.add_argument("--output", default="media_scraper_output", help="Output directory")
    parser.add_argument("--max-pages", type=int, default=60, help="Maximum number of pages to crawl")
    parser.add_argument("--max-assets", type=int, default=300, help="Maximum number of assets to download")
    parser.add_argument("--timeout", type=int, default=20, help="Request timeout in seconds")
    parser.add_argument(
        "--include-keyword",
        action="append",
        default=[],
        help="Additional include keyword for prioritization. Can be passed multiple times.",
    )
    parser.add_argument(
        "--skip-keyword",
        action="append",
        default=[],
        help="Additional skip keyword. Can be passed multiple times.",
    )
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def build_config_from_args(args: argparse.Namespace) -> MediaScraperConfig:
    config = MediaScraperConfig(
        domain=args.domain,
        sitemap_url=args.sitemap,
        output_dir=args.output,
        max_pages=args.max_pages,
        max_assets=args.max_assets,
        timeout=args.timeout,
    )
    if args.include_keyword:
        config.include_keywords.update({k.lower() for k in args.include_keyword})
    if args.skip_keyword:
        config.skip_keywords.update({k.lower() for k in args.skip_keyword})
    return config


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(levelname)s: %(message)s")
    config = build_config_from_args(args)
    scraper = SiteMediaScraper(config)
    stats = scraper.run()
    logging.info("Done. Stats: %s", stats)


if __name__ == "__main__":
    main()
