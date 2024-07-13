import time
from time import sleep
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from utils import retry_func

@retry_func(n_times=1, sleep_time=2)
def get_to_the_next_page(driver):
#     next_button = WebDriverWait(driver, 2).until(
#         EC.presence_of_element_located((By.CLASS_NAME, 'org-jobs-recently-posted-jobs-module__show-all-jobs-btn')))

#     driver.execute_script("arguments[0].click();", next_button)
    search_output = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, 
        "ember-view.link-without-hover-visited.mt5.pv4")))

    driver.get(search_output[0].get_attribute('href'))

@retry_func(n_times=1, sleep_time=2)
def get_company_open_positions(driver, company_link):
    driver.get(company_link + "/jobs")
    sleep(2)
    scroll_script = "window.scrollTo(0, document.body.scrollHeight);"
    driver.execute_script(scroll_script)
    sleep(2)
    
    search_output = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, 
        "ember-view.link-without-hover-visited.mt5.pv4")))
    
    if len(search_output) == 0:
        print("skip job")
        return None
#     print("parse job")
    get_to_the_next_page(driver)
    sleep(2)

    search_output = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
    (By.CLASS_NAME, 
     "job-card-list__entity-lockup.artdeco-entity-lockup.artdeco-entity-lockup--size-4.ember-view")))

    jobs_parsed = []
    for search_output_single in search_output: 
        try:
            org_name = search_output_single.find_element_by_class_name(
                'job-card-container__primary-description').text
            position_name = search_output_single.find_element_by_class_name(
                'disabled.ember-view.job-card-container__link.job-card-list__title.job-card-list__title--link'
            ).find_element_by_class_name('visually-hidden').text

            jobs_parsed.append({
                "org_name": org_name,
                "job_name": position_name
            })
        except:
            pass

    jobs_parsed = pd.DataFrame(jobs_parsed)

    jobs_parsed['company-link'] = company_link
    return jobs_parsed

@retry_func(n_times=1, sleep_time=2)
def parse_insights(driver, company_link):
    driver.get(company_link + "/insights")
    sleep(3)
    
    scroll_script = "window.scrollTo(0, document.body.scrollHeight);"
    driver.execute_script(scroll_script)
    
    search_output = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 
             "org-insights-module__summary")))[0]
    growth = [i.text for i in search_output.find_elements_by_class_name('visually-hidden')]
    growth = pd.DataFrame({"growth": growth})

    search_output = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 
             "org-insights-module__summary-table-container")))[0].find_elements_by_class_name(
                "org-insights-module__summary-block.t-14.t-black--light.t-normal"
    )
    growth["period"] = [i.text for i in search_output][1:]
    growth['company-link'] = company_link

    search_output_b = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 
             "org-insights-functions-growth__content")))[0]
        

    search_output = search_output_b.find_elements_by_class_name("org-function-growth-table__function-name.org-insights-functions-growth__table-data.t-14.t-black--light.t-normal")
    growth_segments = [i.text for i in search_output]
    
    
   
    
    search_output = search_output_b.find_elements_by_class_name("org-function-growth-table__growth-data.org-insights-functions-growth__table-data.t-14.t-black--light.t-normal")
    
    growth_pcnt = [i.find_element_by_class_name('visually-hidden').text for i in search_output]
    growth_segments = pd.DataFrame({
        "segments": growth_segments,
        "6m": growth_pcnt[::2],
        "12m": growth_pcnt[1::2]
    })
    growth_segments['company-link'] = company_link
    return (growth_segments, growth)