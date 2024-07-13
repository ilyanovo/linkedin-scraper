import time
import pandas as pd
from tqdm import tqdm
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from utils import retry_func

unwanted_words = [
    "new feed updates notifications\nHome", "My Network", "Jobs", "Messaging", "Notifications", "Advertise",
                 "1\n1 new notification\nNotifications", "Status is reachable", "Status is online", "Follow"]

def parse_company(company_block):
    results = {}
    
    config = [
        ("name", "app-aware-link"),
        ("location", "entity-result__primary-subtitle"),
        ("description", "entity-result__summary"),
        ("followers", "entity-result__secondary-subtitle"),
        ("jobs-posed", "reusable-search-simple-insight__text")
    ]
    
    for col_name, class_name in config:
        try:
            results[col_name] = company_block.find_element_by_class_name(class_name).text
        except:
            results[col_name] = None
           
    try:
        results["company-link"] = company_block.find_element_by_class_name("app-aware-link").get_attribute("href")
    except:
        pass
    
    return results


@retry_func()
def parse_page(driver):
    search_output = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "search-marvel-srp")))[0]
    companies_search = search_output.find_elements_by_class_name("entity-result__divider")
    companies_search = [i for i in companies_search if i.text not in unwanted_words]
    tmp_extracted = pd.DataFrame([parse_company(i) for i in companies_search])
    return tmp_extracted

@retry_func()
def get_to_the_next_page(driver):
    next_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Next"]')))
    driver.execute_script("arguments[0].click();", next_button)

def try_convert(x):
    try:
        return float(x)
    except:
        return 100
    
@retry_func()
def parse_request(number_of_pages, number_of_companies_per_page, driver):
    all_organisations_extracted = []
    search_output = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "search-marvel-srp")))[0]

    total_results_found = search_output.find_element_by_class_name("t-black--light").text
    total_results_found = int(
        total_results_found.replace("About", "").replace("results", "").strip().replace(",", ""))

    if total_results_found == 0:
        print("Empty page, skippping")
        return 

    total_pages = min(number_of_pages, int(round(total_results_found / number_of_companies_per_page)))

    page_counter = 0
    for page in tqdm(range(total_pages), desc="Parsing search"):
        if page_counter >= number_of_pages:
            break
        tmp_extracted = parse_page(driver)

        all_organisations_extracted.append(tmp_extracted)
        #Use JavaScript to scroll down the page
        scroll_script = "window.scrollTo(0, document.body.scrollHeight);"
        driver.execute_script(scroll_script)

        ### stop search scrolling when most of the companies on the pages do not have any followers
        if (
            tmp_extracted['followers']
                .str.replace("followers", "")
                .str.replace("follower", "")
                .str.replace("K", "000")
                .str.replace("M", "000000").apply(try_convert).sum()
        ) < 5:
            break
            
        page_counter += 1
        if page_counter >= total_pages:
            break

        #Use JavaScript to press Next button
        get_to_the_next_page(driver)
        time.sleep(1)

    all_organisations_extracted = pd.concat(all_organisations_extracted).reset_index(drop=True)
    return all_organisations_extracted