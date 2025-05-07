import streamlit as st
import json
import os
import asyncio
from crawler import WebCrawler
from parser import DocumentationParser
from postprocessor import OutputCleaner
from dotenv import load_dotenv

load_dotenv()

st.title("Documentation Parser")
st.write("Enter URLs to crawl and parse documentation modules.")

# Input form
with st.form("url_form"):
    urls = st.text_area("Enter URLs (one per line)", height=100)
    max_depth = st.number_input("Max Crawl Depth", min_value=1, max_value=5, value=3)
    max_pages = st.number_input("Max Pages to Crawl", min_value=10, max_value=100, value=50)
    submitted = st.form_submit_button("Crawl and Parse")

async def crawl_urls(urls, max_depth, max_pages):
    """Crawl multiple URLs and return all pages"""
    crawler = WebCrawler(max_depth=max_depth, max_pages=max_pages)
    all_pages = []
    for url in urls:
        pages = await crawler.crawl(url)
        all_pages.extend(pages)
    await crawler.close()
    return all_pages

if submitted and urls:
    urls = [url.strip() for url in urls.split("\n") if url.strip()]
    if not urls:
        st.error("Please enter at least one valid URL.")
    else:
        with st.spinner("Crawling and parsing..."):
            # Initialize components
            parser = DocumentationParser()
            cleaner = OutputCleaner()

            # Run async crawling
            all_pages = asyncio.run(crawl_urls(urls, max_depth, max_pages))

            # Parse pages
            all_modules = []
            for page in all_pages:
                modules = parser.parse_page(page)
                all_modules.extend(modules)

            # Clean output
            cleaned_modules = cleaner.clean_output(all_modules)

            # Display results
            st.subheader("Parsed Documentation Modules")
            st.json(cleaned_modules)

            # Save output
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "documentation_modules.json")
            with open(output_path, "w") as f:
                json.dump(cleaned_modules, f, indent=2)
            st.success(f"Output saved to {output_path}")

            # Add download button for JSON export
            json_data = json.dumps(cleaned_modules, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download Results as JSON",
                data=json_data,
                file_name="documentation_modules.json",
                mime="application/json"
            )
