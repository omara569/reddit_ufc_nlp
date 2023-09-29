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
def parse_posts(reddit_post_path: str, posts_parsed_path: str) -> None:
    dates = os.listdir(reddit_post_path)
    for date in dates:
        date_path = reddit_post_path + '/' + date
        posts = os.listdir(date_path)
        make_dir(posts_parsed_path+'/'+date)
        for post in posts:
            soup = make_soup(date_path+'/'+post)
            image_html = get_image(soup)
            post_text = get_post_text(soup) # Title included
            video_html = get_video(soup)
            post_dir = post.split('.')[0]
            make_dir(posts_parsed_path+'/'+date+'/'+post_dir)
            if post_text is not None:
                with open(posts_parsed_path+'/'+date+'/'+post_dir+'/text.txt', mode='w', encoding='utf-8') as f:
                    f.write(post_text)
            if image_html is not None:
                with open(posts_parsed_path+'/'+date+'/'+post_dir+'/image.html', mode='w', encoding='utf-8') as f:
                    f.write(image_html.prettify())
            if video_html is not None:
                with open(posts_parsed_path+'/'+date+'/'+post_dir+'/video.html', mode='w', encoding='utf-8') as f:
                    f.write(video_html.prettify())                


def get_image(soup:BeautifulSoup) -> str:
    post = soup.find('shreddit-post')
    image_html = post.find('img')
    return image_html


def get_video(soup: BeautifulSoup) -> str:
    video = soup.find('video', class_ = 'bg-black')
    return video


# TODO: Something to implement down the line
def get_comment_text(soup: BeautifulSoup) -> str:
    pass


def get_post_text(soup: BeautifulSoup) -> str:
    post = soup.find('shreddit-post')
    post_title = ' : '.join(soup.find('title').text.split(' : ')[:-1])
    post_text = post.find('div', {'slot':'text-body'})
    text = ''
    if post_text is not None:
        post_text = post_text.find_all('p')    
        for text_block in post_text:
            text += text_block.text
        text = ' '.join(text.split('\n')).strip(' ')
    text = post_title + '\n' + text
    return text


def parser():
    local_path = os.path.dirname(__file__)
    params = get_params()
    # Define the path the posts will be saved to
    posts_path = local_path+params.reddit_posts_dir_name
    dates_collected = os.listdir(posts_path) # Already collected dates

    posts_parsed_path = local_path+params.posts_parsed # Location we'll save the text of a post
    make_dir(posts_parsed_path) 

    print('Starting Parsing')
    parse_posts(posts_path, posts_parsed_path)
    print('Done')


parser()