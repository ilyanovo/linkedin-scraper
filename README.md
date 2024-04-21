# LinkedIn Scraper
A simple tool for parsing LinkedIn data.

Pleaase make sure that you have [Chromedriver](https://googlechromelabs.github.io/chrome-for-testing/#stable) installed.
Additionally, more instructions can be found in the related Medium [article](https://medium.com/@ilya.novoselskiy.y/extracting-and-visualizing-linkedin-data-a-brief-exploration-of-it-positions-in-medium-sized-us-83bd7f394960)

To begin scraping, you should update the parameters in `update.py`:

- number_of_pages: Maximum number of pages to parse.
- company_size: Name of the company size filter from the search query.
- company_industry: Name of the industry from the search query.
- Then run `python3 scrap.py`.

A new Chrome window will open, and you will be redirected to LinkedIn. Authorize, and then press Enter in the console to start parsing.
