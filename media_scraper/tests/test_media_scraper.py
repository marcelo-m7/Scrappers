import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

from bs4 import BeautifulSoup

from media_scraper.main import MediaScraperConfig, SiteMediaScraper


class TestMediaScraper(unittest.TestCase):
    def setUp(self) -> None:
        self.config = MediaScraperConfig(
            domain="https://www.example.com",
            sitemap_url="https://www.example.com/sitemap.xml",
            output_dir="unused",
            max_pages=10,
            max_assets=20,
        )
        self.scraper = SiteMediaScraper(self.config)

    def test_expand_candidate_urls_handles_srcset_and_relative_urls(self) -> None:
        urls = list(
            self.scraper.expand_candidate_urls(
                "/images/a.svg 1x, https://www.example.com/media/b.png 2x",
                "https://www.example.com/product/page",
            )
        )
        self.assertEqual(
            urls,
            [
                "https://www.example.com/images/a.svg",
                "https://www.example.com/media/b.png",
            ],
        )

    def test_filename_normalization(self) -> None:
        filename = self.scraper.build_filename(
            "https://www.example.com/media/UI Mockup Final.svg?x=1",
            "https://www.example.com/apps/awesome page/",
            ".svg",
            "abcdef0123456789",
        )
        self.assertEqual(filename, "apps-awesome-page__ui-mockup-final__abcdef01.svg")

    def test_extract_candidates_and_filtering(self) -> None:
        html = """
        <html><body>
            <img src="/media/product_dashboard.png" alt="ERP dashboard mockup" />
            <img src="/media/favicon.png" alt="favicon" />
            <img src="/media/photo.jpg" alt="photo" />
            <img srcset="/icons/x.svg 1x, /icons/y.svg 2x" alt="ui icon" />
        </body></html>
        """
        soup = BeautifulSoup(html, "html.parser")
        items = self.scraper.extract_media_candidates(soup, "https://www.example.com/page")
        urls = sorted(item["url"] for item in items)
        self.assertEqual(
            urls,
            [
                "https://www.example.com/icons/x.svg",
                "https://www.example.com/icons/y.svg",
                "https://www.example.com/media/product_dashboard.png",
            ],
        )

    def test_duplicate_download_avoids_second_write(self) -> None:
        with TemporaryDirectory() as temp_dir:
            self.scraper.output_dir = Path(temp_dir)
            mock_response = Mock()
            mock_response.content = b"same"
            mock_response.raise_for_status.return_value = None
            self.scraper.session.get = Mock(return_value=mock_response)

            a1 = {"url": "https://www.example.com/media/a.png", "page_url": "https://www.example.com/p", "context": "product"}
            a2 = {"url": "https://www.example.com/media/b.png", "page_url": "https://www.example.com/p", "context": "product"}
            self.scraper.download_asset(a1)
            self.scraper.download_asset(a2)

            files = list(Path(temp_dir).rglob("*.png"))
            self.assertEqual(len(files), 1)
            self.assertEqual(len(self.scraper.downloaded_assets), 1)


if __name__ == "__main__":
    unittest.main()
