from typing import List, Dict
from bs4 import BeautifulSoup
import re

class DocumentationParser:
    def __init__(self):
        self.module_keywords = {
            "Getting Started": ["getting started", "welcome", "onboarding", "setup"],
            "Application Management": ["application", "app", "agent", "license", "browser", "desktop"],
            "User Management": ["user", "employee", "department", "role"],
            "Cost Management": ["cost", "spend", "contract", "license", "optimization", "transaction"],
            "Access Provisioning": ["provisioning", "onboarding", "offboarding"],
            "Access Requests": ["access", "request", "catalog"],
            "Access Reviews": ["review", "audit", "compliance"],
            "Integrations": ["integration", "connect", "api", "sdk"],
            "Workflows and Automations": ["workflow", "automation", "playbook"],
            "Settings": ["setting", "configuration", "saml", "billing", "account"],
            "WordPress Documentation": ["wordpress", "gutenberg", "block", "theme"],
            "Chargebee Documentation": ["chargebee", "billing", "subscription", "payment"],
            "Neo Documentation": ["neo", "knowledge base", "support", "ticket"]
        }

    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and special characters"""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[\n\r]+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII (e.g., soft hyphens)
        return text[:200] if len(text) > 200 else text

    def identify_module(self, title: str, content: str) -> str:
        """Identify the module based on title and content"""
        title_lower = title.lower()
        content_lower = content.lower()
        for module, keywords in self.module_keywords.items():
            if any(keyword in title_lower or keyword in content_lower for keyword in keywords):
                return module
        return "Uncategorized"

    def extract_submodules(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Extract submodules and their descriptions"""
        submodules = {}
        # Try different selectors for different site structures
        for selector in [
            'article', 'section', 'div.article-body', 'div.support-content',
            'div.knowledge-base', 'li', 'h1', 'h2', 'h3', 'a'
        ]:
            elements = soup.select(selector)
            for elem in elements:
                title_elem = elem.find(['h1', 'h2', 'h3', 'a']) or elem
                title = self.clean_text(title_elem.get_text(strip=True))
                if not title or len(title) < 3:
                    continue
                # Get description from next paragraph or content
                desc_elem = elem.find_next(['p', 'div']) or elem
                description = self.clean_text(desc_elem.get_text(strip=True))
                if not description or description == title:
                    description = f"Details for {title}"
                submodules[title] = description
        return submodules

    def parse_page(self, page: Dict[str, str]) -> List[Dict]:
        """Parse a single page and extract documentation modules"""
        url = page["url"]
        html = page["content"]
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        modules = []

        # Extract main title and content
        title_elem = soup.find(['h1', 'title', 'header']) or soup.find('h2')
        main_title = self.clean_text(title_elem.get_text(strip=True)) if title_elem else url
        content = self.clean_text(soup.get_text(strip=True))

        # Identify module
        module_name = self.identify_module(main_title, content)

        # Extract submodules
        submodules = self.extract_submodules(soup, url)

        # Create module entry
        description = content[:100] + "..." if len(content) > 100 else content
        module = {
            "module": module_name,
            "Description": description,
            "Submodule": submodules
        }
        modules.append(module)

        return modules