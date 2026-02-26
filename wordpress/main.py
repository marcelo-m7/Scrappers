import os
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from typing import Optional

class WebScraper:
    """
    A class to scrape data from web pages and save it to JSON files.
    """

    def __init__(self, base_url: str, sitemap_url: str, save_folder: str) -> None:
        """
        Initialize the WebScraper.

        Parameters:
        - base_url (str): The base URL of the website.
        - sitemap_url (str): The URL of the sitemap.
        - save_folder (str): The folder to save scraped data.
        """
        self.base_url = base_url
        self.sitemap_url = sitemap_url
        self.save_folder = save_folder
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def fetch_sitemap_urls(self, sitemap_url: str) -> list:
        """
        Fetch URLs from a single sitemap file.

        Parameters:
        - sitemap_url (str): The URL of the sitemap to fetch.

        Returns:
        - list: A list of URLs from the sitemap.
        """
        try:
            response = requests.get(sitemap_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'xml')
            
            # Check if this is a sitemap index (contains <sitemap> tags)
            sitemap_tags = soup.find_all('sitemap')
            if sitemap_tags:
                # This is a sitemap index, fetch sub-sitemaps recursively
                all_urls = []
                sub_sitemaps = [loc.text for loc in soup.find_all('loc')]
                print(f"Found sitemap index with {len(sub_sitemaps)} sub-sitemaps.")
                for sub_sitemap in sub_sitemaps:
                    print(f"  Fetching: {sub_sitemap}")
                    all_urls.extend(self.fetch_sitemap_urls(sub_sitemap))
                return all_urls
            else:
                # This is a regular sitemap with URLs
                return [loc.text for loc in soup.find_all('loc')]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sitemap {sitemap_url}: {e}")
            return []

    def fetch_sitemap(self) -> list:
        """
        Fetch all URLs from the sitemap (handles sitemap indexes).

        Returns:
        - list: A list of page URLs from the sitemap.
        """
        all_urls = self.fetch_sitemap_urls(self.sitemap_url)
        # Filter out XML sitemaps from the final list
        page_urls = [url for url in all_urls if not url.endswith('.xml')]
        return page_urls

    def extract_data(self, url: str) -> Optional[dict]:
        """
        Extract title, content, and metadata from a web page.

        Parameters:
        - url (str): The URL of the web page.

        Returns:
        - dict: A dictionary containing the extracted data.
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            # Check if the response content type is HTML
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            if content_type != 'text/html':
                print(f"Skipping {url} - Not HTML content")
                return None

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove the cookies notification div
            cookies_notification = soup.find('div', id='cookies-notification')
            if cookies_notification:
                cookies_notification.decompose()

            # Remove the footer
            footer = soup.find('footer')
            if footer:
                footer.decompose()

            # Select relevant elements: title and text content
            title = soup.title.text if soup.title else ''
            
            # Extract text from all paragraphs
            text = ' '.join([p.text for p in soup.find_all('p')])
            
            # Extract content from the team-container div
            team_container = soup.find('div', class_='team-container')
            team_content = team_container.get_text(separator=' ', strip=True) if team_container else ''
            
            # Combine the text and team content
            combined_content = f"{text}\n{team_content}"

            # Add metadata: URL
            metadata = {'url': url}

            return {'title': title, 'content': combined_content, 'metadata': metadata}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def save_to_json(self, data: dict, url: str) -> None:
        """
        Save extracted data to a JSON file.

        Parameters:
        - data (dict): The data to save.
        - url (str): The URL of the web page.
        """
        # Create the save folder if it doesn't exist
        os.makedirs(self.save_folder, exist_ok=True)
        
        parsed_url = urlparse(url)
        file_name = f"{parsed_url.netloc.replace('.', '_')}_{parsed_url.path.replace('/', '_')}.json"
        file_name = file_name.strip('_')  # Clean up leading/trailing underscores
        file_path = os.path.join(self.save_folder, file_name)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4, separators=(',', ': '))
            print(f"Data saved to {file_path}")
        except OSError as e:
            print(f"Error saving file {file_path}: {e}")

    def process_url(self, url: str) -> None:
        """
        Process a single URL: extract data and save to JSON.

        Parameters:
        - url (str): The URL to process.
        """
        data = self.extract_data(url)
        if data:
            self.save_to_json(data, url)

    def process_site(self) -> None:
        """Process all URLs from the sitemap."""
        urls = self.fetch_sitemap()
        if not urls:
            print("No URLs found in sitemap.")
            return
        
        total = len(urls)
        print(f"Found {total} URLs to process.")
        
        for index, url in enumerate(urls, 1):
            print(f"Processing ({index}/{total}): {url}")
            self.process_url(url)


def web_scraper_start(base_url='https://dspa.pt/', 
                      sitemap_url='https://dspa.pt/sitemap.xml', 
                      save_folder='web_scraper_files') -> None:
    """
    Initialize and run the web scraper with the given optional parameters.

    Parameters:
    - base_url (str): The base URL of the website.
    - sitemap_url (str): The URL of the sitemap.
    - save_folder (str): The folder to save scraped data.
    """
    try:
        scraper = WebScraper(base_url, sitemap_url, save_folder)
        scraper.process_site()
        print("Web scraping completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"The path '{save_folder}' has not been changed.")


if __name__ == "__main__":
    web_scraper_start()
    