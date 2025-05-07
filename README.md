# Doc-Crawler

It is a Python-based web crawler designed to extract and summarize documentation from specified URLs. It processes the content to provide concise summaries, making it easier for users to understand the key points of technical documents.

## Features

- **Web Crawling**: Efficiently fetches content from provided URLs.
- **Content Parsing**: Extracts meaningful information from the crawled pages.
- **Summarization**: Generates concise summaries of the extracted content.
- **Modular Design**: Utilizes separate modules for crawling, parsing, and summarizing, ensuring maintainability and scalability.

## Project Structure

The repository contains the following key files:

- `app.py`: The main application file that integrates the crawling, parsing, and summarizing functionalities.
- `crawler.py`: Handles the web crawling logic, fetching content from URLs.
- `parser.py`: Parses the fetched content to extract relevant information.
- `postprocessor.py`: Processes the parsed data for further use.
- `summarizer.py`: Generates summaries from the processed data.
- `requirements.txt`: Lists the necessary Python packages for the project.

## Installation

To set up the project locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/kunal534/doc-crawler.git
   cd doc-crawler
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt

3. To run the application:
   ```bash
   streamlist app.py

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. Ensure that your code adheres to the existing coding standards and includes appropriate tests.
