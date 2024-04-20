import time
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from utils import retry_func

@retry_func(n_times=1, sleep_time=5)
def get_profile_base_info(user_block):
    results = {}
    
    user_profile_single = user_block.find_elements_by_class_name('artdeco-entity-lockup__content')[0]
    
    config = [
        ("name", "app-aware-link"),
        ("description", "t-14"),
    ]
    
    for col_name, class_name in config:
        try:
            results[col_name] = user_profile_single.find_element_by_class_name(class_name).text
        except:
            results[col_name] = None
           
    try:
        results["profile-link"] = user_profile_single.find_element_by_class_name("app-aware-link").get_attribute("href")
    except:
        pass
    
    try:
        results["followers"] = user_block.find_elements_by_class_name("text-align-center")[0].text
    except:
        pass
    return results

@retry_func(n_times=2, sleep_time=5)
def get_company_workers(driver, link):
    driver.get(link + "people/")
    total_attempts = 0 
    max_profiles = 0 
    while True:
        scroll_script = "window.scrollTo(0, document.body.scrollHeight);"
        driver.execute_script(scroll_script)

        search_output = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "scaffold-finite-scroll__content")))[0]

        all_users_extracted = search_output.find_elements_by_class_name("org-people-profile-card__profile-info")

        if len(all_users_extracted) > max_profiles:
            max_profiles = len(all_users_extracted)
            total_attempts = 0
        else:
            total_attempts += 1
            time.sleep(4)

        if total_attempts >= 2:
            break

    tmp_extracted = pd.DataFrame([get_profile_base_info(i) for i in all_users_extracted])
    return tmp_extracted