import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from typing import List
from datetime import date
from datetime import datetime, timedelta
from time import sleep
from structures.config import get_params


def make_dir(current_directory: str) -> bool:
    doesExist = os.path.exists(current_directory)
    if not doesExist:
        os.makedirs(current_directory)
    return doesExist


def driver_instance(driver_file_name=None) -> webdriver.firefox.webdriver.WebDriver:
    firefox_options = Options()
    firefox_options.add_argument('-headless')
    if driver_file_name is not None: # We only perform this at the start
        if driver_file_name in os.listdir(os.getcwd()):
            os.remove(os.getcwd()+'/'+driver_file_name)
    return webdriver.Firefox(options=firefox_options)


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
    post_dates = os.path.dirname(__file__) 
    dir_list = None
    if 'reddit_posts' in os.listdir(post_dates):
        post_dates = post_dates + '/reddit_posts'
        dir_list = os.listdir(post_dates)

    last_recorded_post = None
    scroll_counter = 0
    while not last_post_date:
        for i in range(10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Execute this line 10 times

        post_elements = driver.find_elements(By.CSS_SELECTOR, 'a.absolute.inset-0')
        # Open the lastest post on the page. Check it's date and if it's 6 months prior to the desired date, we can stop scrolling and exit
        driver2 = driver_instance()
        open_url(post_elements[-1].get_attribute('href'), driver2)
        latest_post_date = driver2.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime').split('T')[0]
        latest_post_date = datetime.strptime(latest_post_date, '%Y-%m-%d').date()
        driver2.quit()

        if last_recorded_post is not None:
            if last_recorded_post == latest_post_date:
                scroll_counter += 1
                if scroll_counter == 10:
                    break
            else:
                last_recorded_post = latest_post_date
                scroll_counter = 0
        else:
            last_recorded_post = latest_post_date
        if latest_post_date < date_in_past :
            last_post_date = True
        if dir_list is not None:
            if latest_post_date in dir_list:
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

        date_post = driver.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime').split('T')
        date_post[-1] = date_post[-1].split('.')[0]
        date_post[-1] = ''.join(date_post[-1].split(':'))
        date_post = ' '.join(date_post)
        save_name = date_post + save_name #Name of file
        date_post = date_post.split(' ')[0]
        make_dir(reddit_posts+date_post) #Makes folder for that date

        save_name = reddit_posts + date_post+'/'+save_name
        if os.path.exists(save_name):
            break

        with open(save_name, mode='w', encoding='utf-8') as f:
            f.write(driver.page_source)

        counter += 1
        if counter == 20:
            driver.quit()
            driver, counter = driver_instance(), 0


def fighter_list(url: str, local_path: str):
    driver = driver_instance()
    open_url(url, driver)
    sleep(2)
    close_button = driver.find_element(By.CSS_SELECTOR, 'button.onetrust-close-btn-handler.onetrust-close-btn-ui.banner-close-button.ot-close-icon')
    sleep(2)
    close_button.click()
    # Endless scrolling
    counter = 0
    while counter != 10:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            driver.find_element(By.CSS_SELECTOR, 'a.button').click()
            sleep(1)
            counter = 0
        except:
            counter += 1
    
    # Done scrolling, now get the list of names
    elements = driver.find_elements(By.CSS_SELECTOR, 'span.c-listing-athlete__name')

    fighter_names = {element.text for element in elements} #Set of Fighter Names
    driver.quit()
    with open(local_path+'/fighter_names.txt', mode = 'w', encoding = 'utf-8') as f:
        for item in fighter_names:
            f.write(item + '\n')
    

def scraper(params=get_params()):
    local_path = os.path.dirname(__file__) # Returns the working directory of this script

    print('Getting List of Fighter Names')
    fighter_list(params.fighter_list_url, local_path)

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
    driver.quit()
    
    print('Opening Posts and Saving to Local Machine')
    collect_data(post_urls, local_path)

    print('Completed Scrape')


scraper()