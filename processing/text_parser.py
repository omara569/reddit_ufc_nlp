from bs4 import BeautifulSoup
import pandas as pd
import os
from typing import Any, List, Tuple
from structures.config import get_params


def make_dir(directory: str) -> None:
    doesExist = os.path.exists(directory)
    if not doesExist:
        os.makedirs(directory)


def make_soup(file_path: str) -> BeautifulSoup:
    with open(file_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    return soup


# TODO: Make this go through all the posts and save them to directories
def parse_post_text(reddit_post_path: str) -> None:
    soup = make_soup(reddit_post_path)
    post_title = get_title(soup)
    image_html = get_image(soup)
    post_text = get_post_text(soup)
    pass


def get_title(soup: BeautifulSoup) -> str:
    title_element = soup.find('title')
    return title_element.text


def get_image(soup:BeautifulSoup) -> str:
    post = soup.find('shreddit-post')
    image_html = post.find('img')
    return image_html


# TODO: Something to implement down the line
def get_comment_text(soup: BeautifulSoup) -> str:
    pass


def get_video(soup: BeautifulSoup) -> str:
    video = soup.find('video', class_ = 'bg-black')
    return video


def get_post_text(soup: BeautifulSoup) -> str:
    post = soup.find('shreddit-post')
    post_text = post.find('div', {'slot':'text-body'}).text
    return post_text


def parser():
    local_path = os.path.dirname(__file__)
    params = get_params()

    posts_path = local_path+params.reddit_posts_dir_name
    dates_collected = os.listdir(posts_path)

    posts_parsed_path = local_path+params.posts_text_parsed
    make_dir(posts_parsed_path)

    tst_post_path = 'C:/Users/omara/Desktop/workspace/mma_nlp/processing/reddit_posts/2023-09-22/2023-09-22 115723rufccomments16p8dmocontaminated_supplements.html'
    parse_post_text(tst_post_path)






parser()