import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from typing import Any, List, Tuple
from time import sleep
from datetime import date
from datetime import datetime, timedelta
from structures.config import get_params


def make_dir(current_directory: str) -> None:
    doesExist = os.path.exists(current_directory)
    if not doesExist:
        os.makedirs(current_directory)


def driver_instance(driver_file_name=None) -> webdriver.firefox.webdriver.WebDriver:
    if driver_file_name is not None: # We only perform this at the start
        if driver_file_name in os.listdir(os.getcwd()):
            os.remove(os.getcwd()+'/'+driver_file_name)
    return webdriver.Firefox()


def open_url(url: str, driver: webdriver.firefox.webdriver.WebDriver) -> None:
    driver.get(url)


# Function to click the "sort by" feature on the reddit posts
def sort_posts(driver: webdriver.firefox.webdriver.WebDriver) -> None:
    elements = driver.find_elements(By.CSS_SELECTOR, 'div') 
    sort_by_element = [sub_element for sub_element in elements if "Sort By" in sub_element.text][-1]
    sort_by_element.click()
    elements = driver.find_elements(By.CSS_SELECTOR, 'div')
    sort_by_elements = [sub_element for sub_element in elements if sub_element.get_attribute('slot')=='dropdown-items'][0]
    sort_by_element = [sub_element for sub_element in sort_by_elements.find_elements(By.CSS_SELECTOR, 'li') if 'New' in sub_element.text][0]
    sort_by_element.click()


def change_format(driver: webdriver.firefox.webdriver.WebDriver) -> None:
    element = driver.find_element(By.CSS_SELECTOR, 'shreddit-layout-event-setter')
    element.click()
    elements = driver.find_elements(By.CSS_SELECTOR, 'li')
    element = [sub_element for sub_element in elements if 'Classic' in sub_element.text][0]
    element.click()


def scroll_down(driver: webdriver.firefox.webdriver.WebDriver, date_in_past: datetime.date) -> None:
    # We want to scroll down until we reach posts that are more than 6 months ago
    last_post_date = False  # Indicates whether or not the last post is the distance required from the current date
    while not last_post_date:
        for i in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Execute this line 10 times

        post_elements = driver.find_elements(By.CSS_SELECTOR, 'a.absolute.inset-0')
        # Open the lastest post on the page. Check it's date and if it's 6 months prior to the desired date, we can stop scrolling and exit
        driver2 = driver_instance()
        open_url(post_elements[-1].get_attribute('href'), driver2)
        latest_post_date = driver2.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime').split('T')[0]
        latest_post_date = datetime.strptime(latest_post_date, '%Y-%m-%d').date()
        driver2.close()
        if latest_post_date < date_in_past:
            last_post_date = True


def collect_posts(driver: webdriver.firefox.webdriver.WebDriver) -> List[str]:
    post_elements = driver.find_elements(By.CSS_SELECTOR, 'a.absolute.inset-0')
    post_urls = [element.get_attribute('href') for element in post_elements]
    return post_urls


def collect_data(urls: List[str], local_path: str) -> None:
    driver = driver_instance()
    counter = 0
    reddit_posts = local_path + '/' + 'reddit_posts/'
    make_dir(reddit_posts)

    for url in urls:
        splitted = url.split('.com')[-1]
        splitted = splitted.split('/')
        save_name = ''.join(splitted)+'.html'
        open_url(url, driver)

        date_post = driver.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime').split('T')[0]
        sub_dir = reddit_posts + date_post+'/'
        make_dir(sub_dir)

        with open(sub_dir+save_name, mode='w', encoding='utf-8') as f:
            f.write(driver.page_source)

        counter += 1
        if counter == 20:
            driver.close()
            driver, counter = driver_instance(), 0


def scraper(params=get_params()):
    local_path = os.path.dirname(__file__) # Returns the working directory of this script

    print('Opening Reddit')
    driver = driver_instance(params.gecko_driver_file_name)
    driver.get(params.reddit_page)

    print('Formatting Elements')
    sort_posts(driver)
    change_format(driver) # Classic format - takes up less real-estate in the browser
    
    print('Loading Elements')
    current_date = date.today()
    load_to_date = None
    if not params.initial_run:
        last_date = local_path + '/reddit_posts/'
        load_to_date = os.listdir(last_date)[-2].date()
    else:
        load_to_date = current_date - timedelta(days=params.days_prior)
    scroll_down(driver, load_to_date)
    
    print('Collecting Post URLs')
    post_urls = collect_posts(driver)
    driver.close()
    
    print('Opening Posts and Saving to Local Machine')
    collect_data(post_urls, local_path)
        


scraper()