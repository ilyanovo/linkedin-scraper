import time
from selenium import webdriver
import pandas as pd
from tqdm.notebook import tqdm

from parse_search import parse_request
from parse_company import get_company_workers

search_url = "https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22103644278%22%5D&companySize={companySize}&"\
    "industryCompanyVertical={industryCompanyVertical}&origin=FACETED_SEARCH&sid=z77"
number_of_pages = 99
number_of_companies_per_page = 10 # number of companies on linkedin search page
company_size = "%5B%22E%22%5D" #stands for "200 - 500" company size
company_industry = "%5B%222468%22%5D" #stands for "Electrical Equipment Manufacturing"


def get_companies(driver):
    all_organizations_extracted = []
    driver.get(search_url.format(
        companySize=company_size, 
        industryCompanyVertical=company_industry))
    all_organizations_extracted = parse_request(number_of_pages, number_of_companies_per_page, driver)
    all_organizations_extracted = all_organizations_extracted[
        ~all_organizations_extracted['company-link'].isna()].reset_index(drop=True)
    return all_organizations_extracted


def parse_companies(driver, company_links: list[str]):
    total_workers_parsed = []
    for link in tqdm(company_links, desc="Parsing companies"):
        tmp_extracted = get_company_workers(driver, link)
        print("DONE")
        if tmp_extracted is None:
            continue

        tmp_extracted['company-link'] = link
        total_workers_parsed.append(tmp_extracted)
    total_workers_parsed_prep = pd.concat(total_workers_parsed).reset_index(drop=True)
    return total_workers_parsed_prep


def main():
    opts = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=opts)
    driver.maximize_window()
    time.sleep(4)

    driver.get('https://www.linkedin.com/in/ilya-novoselskiy-2493a269') #any linkedin url will work
    input('Press Enter to continue')
    all_organizations_extracted = get_companies(driver)

    all_workers = parse_companies(driver, all_organizations_extracted['company-link'].values)
    all_organizations_extracted.to_csv("companies.csv", index=False)
    all_workers.to_csv("workers.csv", index=False)
    

if __name__ == "__main__":
    main()