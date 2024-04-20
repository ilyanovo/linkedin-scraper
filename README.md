# LinkedIn Scraper
A simple tool for parsing LinkedIn data.

To begin scraping, you should update the parameters in `update.py`:

- number_of_pages: Maximum number of pages to parse.
- company_size: Name of the company size filter from the search query.
- company_industry: Name of the industry from the search query.
- Then run `python3 scrap.py`.

A new Chrome window will open, and you will be redirected to LinkedIn. Authorize, and then press Enter in the console to start parsing.