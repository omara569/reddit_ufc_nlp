import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from typing import Any, List, Tuple
from time import sleep
from datetime import date
from datetime import datetime, timedelta
from structures.config import get_params


def driver_instance() -> webdriver.firefox.webdriver.WebDriver:
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


def scroll_down(driver: webdriver.firefox.webdriver.WebDriver, current_date: date) -> None:
    # We want to scroll down until we reach posts that are more than 6 months ago
    last_post_date = False  # Indicates whether or not the last post is the distance required from the current date
    six_months_ago = current_date - timedelta(days=183)
    while not last_post_date:
        for i in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Execute this line 10 times

        post_elements = driver.find_elements(By.CSS_SELECTOR, 'a.absolute.inset-0')
        # Open the lastest post on the page. Check it's date and if it's 6 months prior to the desired date, we can stop scrolling and exit
        driver2 = driver_instance()
        open_url(post_elements[-1].get_attribute('href'), driver2)
        latest_post_date = driver2.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime').split('T')[0]
        latest_post_date = datetime.strptime(latest_post_date, '%Y-%m-%d').date()
        if latest_post_date < six_months_ago:
            last_post_date = True


def collect_posts(driver: webdriver.firefox.webdriver.WebDriver) -> List[str]:
    post_elements = driver.find_elements(By.CSSSELECTOR, 'a.absolute.inset-0')
    post_links = [element.get_attribute('href') for element in post_elements]
    return post_links


def scraper():
    params = get_params()
    driver = driver_instance()
    driver.get(params.reddit_page)
    # Setup reddit page format
    sort_posts(driver)
    change_format(driver) # Classic format - takes up less real-estate in the browser

    current_date = date.today()
    scroll_down(driver, current_date)

    post_links = collect_posts(driver)
    


scraper()