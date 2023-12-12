import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from typing import List
from datetime import date, datetime, timedelta
from time import sleep
from psutil import process_iter
import requests
from bs4 import BeautifulSoup 
from structures.config import get_params


# Create directoreis as needed
def make_dir(current_directory: str) -> bool:
    doesExist = os.path.exists(current_directory)
    if not doesExist:
        os.makedirs(current_directory)
    return doesExist


# Kills existing instances of the selenium web browser to avoid any issues with processes in use
def kill_existing(): # kills existing instances of the geckodriver for firefox
    for proc in process_iter(['pid', 'name', 'open_files']):
        if proc.info['open_files'] is not None:
            for file in proc.info['open_files']:
                if 'geckodriver.log' in file.path.lower():
                    proc.kill()
    sleep(1)


# Creates an instance of the web browser
def driver_instance(driver_file_name=None, kill_existing_bool=False) -> webdriver.firefox.webdriver.WebDriver:
    if kill_existing_bool:
        kill_existing()
    firefox_options = Options()
    firefox_options.add_argument('-headless')
    if driver_file_name is not None: # We only perform this at the start
        if driver_file_name in os.listdir(os.getcwd()):
            os.remove(os.getcwd()+'/'+driver_file_name)
    return webdriver.Firefox(options=firefox_options)


# Opens URL
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
    sleep(1)


# Function to select the "classic" layout feature on the reddit posts
def change_format(driver: webdriver.firefox.webdriver.WebDriver) -> None:
    element = driver.find_element(By.CSS_SELECTOR, 'shreddit-layout-event-setter')
    element.click()
    elements = driver.find_elements(By.CSS_SELECTOR, 'li')
    sleep(1) # Give it a second to refresh
    element = [sub_element for sub_element in elements if 'Classic' in sub_element.text][0]
    element.click()


# Sign in with Google box needs to be closed
def close_signin(driver: webdriver.firefox.webdriver.WebDriver) -> None:
    sleep(1)
    credentials_element = driver.find_element(By.ID, 'credential_picker_container')
    iframe = credentials_element.find_element(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(iframe)
    close_element = driver.find_element(By.ID, 'close')
    close_element.click()
    driver.switch_to.default_content()
    sleep(1)


# Scrolls down the page and utilizes Beautiful Soup parsing to work around unresponsive target machines (needed for dealing with dynamic HTML)
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

        # post_elements = driver.find_elements(By.CSS_SELECTOR, 'a.absolute.inset-0') # Using selenium
        page_source = driver.page_source    # Using BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        post_elements = soup.find_all('a', class_='absolute inset-0')
        href = 'https://www.reddit.com' + post_elements[-1]['href']
        # Open the lastest post on the page. Check it's date and if it's 6 months prior to the desired date, we can stop scrolling and exit
        driver2 = driver_instance()
        # href = post_elements[-1].get_attribute('href')
        open_url(href, driver2)
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


# Collect the urls of the posts loaded onto the page
def collect_posts(driver: webdriver.firefox.webdriver.WebDriver) -> List[str]:
    post_elements = driver.find_elements(By.CSS_SELECTOR, 'a.absolute.inset-0')
    post_urls = [element.get_attribute('href') for element in post_elements]
    return post_urls


# Save post HTML to local machine
def collect_data(urls: List[str], local_path: str) -> None:
    driver = driver_instance()
    counter = 0
    reddit_posts = local_path + '/' + 'reddit_posts/'
    make_dir(reddit_posts)
    comment_counter = 0 # Used in instances where we need to create a new name for the post that the below methodology doesn't work for (i.e. Try-except)
    for url in urls:
        splitted = url.split('.com')[-1]
        splitted = splitted.split('/')
        save_name = ''.join(splitted)+'.html'
        open_url(url, driver)
        
        try:
            date_post = driver.find_element(By.CSS_SELECTOR, 'time').get_attribute('datetime').split('T')
        except NoSuchElementException:
            continue # Skip posts that don't have a date defined on their HTML
        
        date_post[-1] = date_post[-1].split('.')[0]
        date_post[-1] = ''.join(date_post[-1].split(':'))
        date_post = ' '.join(date_post)
        save_name = date_post + save_name #Name of file
        date_post = date_post.split(' ')[0]
        make_dir(reddit_posts+date_post) #Makes folder for that date

        save_name = reddit_posts + date_post+'/'+save_name
        if os.path.exists(save_name):
            break

        try:
            with open(save_name, mode='w', encoding='utf-8') as f:
                f.write(driver.page_source)
        except OSError:
            save_name = reddit_posts + date_post + '/new_name_post ' + str(comment_counter) + '.html'
            with open(save_name, mode='w', encoding='utf-8') as f:
                f.write(driver.page_source)
            comment_counter += 1

        counter += 1
        if counter == 20:
            driver.quit()
            driver, counter = driver_instance(), 0


# Obtain all existing fighters in UFC and saving as a text list. Also obtains all fighter images
def fighter_list(url: str, local_path: str):
    print('Getting List of Fighter Names')
    day_val = date.today().isoweekday() # Monday is one and Sunday is 7. We want this to run on every Saturday
    if day_val==6:
        driver = driver_instance(kill_existing_bool=True)
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
        
        # Done scrolling, now get the list of names and images
        fighter_images_dir = local_path + '/fighter_images'
        make_dir(fighter_images_dir)
        elements = driver.find_elements(By.CSS_SELECTOR, 'div.c-listing-athlete-flipcard__front')
        name_elements = [element.find_element(By.CSS_SELECTOR, 'span.c-listing-athlete__name') for element in elements]
        names = [element.text for element in name_elements]
        thumbnail_elements = driver.find_elements(By.CSS_SELECTOR, 'div.c-listing-athlete__thumbnail')
        image_urls = []
        for sub_element in thumbnail_elements:
            try:
                image_urls.append(sub_element.find_element(By.CSS_SELECTOR, 'img').get_attribute('src'))
            except NoSuchElementException:
                image_urls.append(None)

        fighter_names = {element for element in names} #Set of Fighter Names
        driver.quit()

        # Text file containing fighter names
        with open(local_path+'/fighter_names.txt', mode = 'w', encoding = 'utf-8') as f:
            for item in fighter_names:
                f.write(item + '\n')
        # Saving the images as well
        for idx, url in enumerate(image_urls):
            if url is not None:
                response = requests.get(url)
                if response.status_code == 200:
                    image_content = response.content
                    file_path = fighter_images_dir + '/' + names[idx] + '.png'
                    with open(file_path, 'wb') as file:
                        file.write(image_content)
        sleep(1)
    

# Scrape UFC reddit
def scraper(params=get_params()):
    local_path = os.path.dirname(__file__) # Returns the working directory of this script

    fighter_list(params.fighter_list_url, local_path)

    print('Opening Reddit')
    driver = driver_instance(params.gecko_driver_file_name, kill_existing_bool=True)
    driver.get(params.reddit_page)
    close_signin(driver)

    print('Sorting Posts')
    sort_posts(driver)
    print('Formatting Elements')
    change_format(driver) # Classic format - takes up less real-estate in the browser
    
    print('Loading Elements')
    current_date = date.today()
    load_to_date = None
    if not params.initial_run:
        last_date = local_path + '/reddit_posts/'
        load_to_date = datetime.strptime(os.listdir(last_date)[-2], '%Y-%m-%d').date()
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