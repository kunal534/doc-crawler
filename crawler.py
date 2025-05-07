import httpx
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self, max_depth: int = 3, max_pages: int = 50):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        self.pages: List[Dict[str, str]] = []
        self.client = httpx.AsyncClient(follow_redirects=True, timeout=10.0)
        logging.basicConfig(level=logging.INFO)

    async def fetch_page(self, url: str) -> tuple[str, str]:
        """Fetch page content and return URL and HTML content"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return url, response.text
        except httpx.HTTPError as e:
            logging.error(f"Failed to fetch {url}: {e}")
            return url, ""

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all valid links from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                links.append(absolute_url)
        return links

    async def crawl_page(self, url: str, depth: int = 0):
        """Recursively crawl a page and its links"""
        if depth > self.max_depth or len(self.pages) >= self.max_pages or url in self.visited:
            return

        self.visited.add(url)
        logging.info(f"Crawling {url} at depth {depth}")
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc

        url, html = await self.fetch_page(url)
        if not html:
            return

        self.pages.append({"url": url, "content": html})
        
        if depth < self.max_depth:
            links = self.extract_links(html, url)
            for link in links:
                link_domain = urlparse(link).netloc
                if link_domain == base_domain and link not in self.visited:
                    await self.crawl_page(link, depth + 1)

    async def crawl(self, start_url: str) -> List[Dict[str, str]]:
        """Start crawling from the given URL"""
        self.visited.clear()
        self.pages.clear()
        parsed = urlparse(start_url)
        if not parsed.scheme or not parsed.netloc:
            logging.error(f"Invalid URL: {start_url}")
            return []
        
        await self.crawl_page(start_url)
        logging.info(f"Crawled {len(self.pages)} pages")
        return self.pages

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        logging.info("HTTP client closed")