import time, os
from selenium import webdriver
import pandas as pd
import argparse
from tqdm.notebook import tqdm

from parse_search import parse_request
from parse_company import get_company_workers

from parse_company_insights import get_company_open_positions, parse_insights

search_url = "https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22103644278%22%5D&companySize={companySize}&"\
    "industryCompanyVertical={industryCompanyVertical}&origin=FACETED_SEARCH&sid=z77"
number_of_pages = 150
number_of_companies_per_page = 10 # number of companies on linkedin search page

company_size_list = [
    ("200_500", "%5B%22E%22%5D"), 
    ("500_1000", "%5B%22F%22%5D")
]  # %5B%22F%22%5D"- 500-1000 %5B%22G%22%5D - 1000-5000 %5B%22E%22%5D - 200-500
company_industry_default = "%5B%2242%22%5D" #stands for "Insurance"




def get_companies(driver, company_size, company_industry):
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
    job_positions_list = []
    extra_information_gr = []
    extra_information_gr_sgm = []
    for link in tqdm(company_links, desc="Parsing companies"):
        tmp_extracted = get_company_workers(driver, link)
        job_positions_list.append(get_company_open_positions(driver, link))
        insights = parse_insights(driver, link)

        if insights is None:
            growth_segments = None
            growth = None
        else:
            growth_segments, growth = insights
            extra_information_gr.append(growth)
            extra_information_gr_sgm.append(growth_segments)

        if tmp_extracted is not None:
            tmp_extracted['company-link'] = link
            total_workers_parsed.append(tmp_extracted)

        
    total_workers_parsed_prep = pd.concat(total_workers_parsed).reset_index(drop=True)
    job_positions_list = pd.concat(job_positions_list).reset_index(drop=True)
    extra_information_gr = pd.concat(extra_information_gr).reset_index(drop=True)
    extra_information_gr_sgm = pd.concat(extra_information_gr_sgm).reset_index(drop=True)
    return total_workers_parsed_prep, job_positions_list, extra_information_gr, extra_information_gr_sgm


def main(args):
    os.makedirs(args.output_folder, exist_ok=True)
    opts = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=opts)
    driver.maximize_window()
    time.sleep(4)

    driver.get('https://www.linkedin.com/in/ilya-novoselskiy-2493a269') #any linkedin url will work
    input('Press Enter to continue')

    for company_size_name, company_size in company_size_list:
        all_organizations_extracted = get_companies(driver, company_size, args.industry)
        all_organizations_extracted.to_csv(
            os.path.join(args.output_folder, f"companies__{company_size_name}.csv"), index=False)

        all_workers, job_positions_list, extra_information_gr, extra_information_gr_sgm = parse_companies(
            driver, all_organizations_extracted['company-link'].values)
        all_workers.to_csv(os.path.join(args.output_folder, f"workers__{company_size_name}.csv"), index=False)
        job_positions_list.to_csv(os.path.join(args.output_folder, f"job_positions__{company_size_name}.csv"), index=False)
        extra_information_gr.to_csv(os.path.join(args.output_folder, f"extra_information_gr__{company_size_name}.csv"), index=False)
        extra_information_gr_sgm.to_csv(os.path.join(args.output_folder, f"extra_information_gr_sgm__{company_size_name}.csv"), index=False)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_folder", default="output")
    parser.add_argument("--industry", default=company_industry_default)
    args = parser.parse_args()
    main(args)