from bs4 import BeautifulSoup
import os
from structures.config import get_params


# Make directories as needed
def make_dir(directory: str) -> None:
    doesExist = os.path.exists(directory)
    if not doesExist:
        os.makedirs(directory)


# Turn HTML into BeautifulSoup object
def make_soup(file_path: str) -> BeautifulSoup:
    with open(file_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    return soup


# Parse text of each individual reddit post scraped 
def parse_posts(reddit_post_path: str, posts_parsed_path: str) -> None:
    dates = os.listdir(reddit_post_path)
    for date in dates:
        date_path = reddit_post_path + '/' + date
        posts = os.listdir(date_path)
        make_dir(posts_parsed_path+'/'+date)
        for post in posts:
            soup = make_soup(date_path+'/'+post)
            image_html = get_image(soup)
            post_text = get_post_text(soup) # Title included. Gets the comment text as well!
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


# TODO: Fetch the images - not just HTML - image to be used with computer vision to recognize fighters and read any text in memes to gather sentiment
def get_image(soup:BeautifulSoup) -> str:
    post = soup.find('shreddit-post')
    image_html = post.find('img')
    return image_html


# TODO: Fetch the video - not just HTML - similar to "get_image" function purpose, but with video instead
def get_video(soup: BeautifulSoup) -> str:
    video = soup.find('video', class_ = 'bg-black')
    return video


# Obtain the text of each comment on a reddit post
def get_comment_text(soup: BeautifulSoup) -> str:
    comment_elements = soup.find_all('shreddit-comment')
    bag_of_text = ''
    for comment in comment_elements:
        if not comment:
            continue
        author = comment['author']
        if author == '[deleted]':
            continue
        timestamp = comment.find('faceplate-timeago')['ts']
        comment_text = comment.find('div', {'slot':'comment'}).text
        bag_of_text += author + ' replied at ' + timestamp + ':\n' + comment_text + '\n'

    return bag_of_text


# Obtain the text of the reddit post. This is the initial post and the comments from "get_comment_text"
def get_post_text(soup: BeautifulSoup) -> str:
    post = soup.find('shreddit-post')
    post_title = ' : '.join(soup.find('title').text.split(' : ')[:-1])
    poster = post.find('span', {'slot':'authorName'}).text.strip('\n')
    post_time = post['created-timestamp']
    post_text = post.find('div', {'slot':'text-body'})
    starting_text = poster + ' posted at ' + post_time + ':\n'
    text = ''
    if post_text is not None:
        post_text = post_text.find_all('p')    
        for text_block in post_text:
            text += text_block.text
        text = ' '.join(text.split('\n')).strip(' ')
    text += post_title + '\n' + text
    comment_text = get_comment_text(soup)
    text = starting_text + text + '\n' + comment_text
    return text


def parser():
    root_path = os.getcwd()
    params = get_params()
    # Define the path the posts will be saved to
    posts_path = root_path + '/' +params.reddit_posts_dir_name

    posts_parsed_path = root_path + '/' +params.posts_parsed # Location we'll save the text of a post
    make_dir(posts_parsed_path) 

    print('Starting Parsing')
    parse_posts(posts_path, posts_parsed_path)
    print('Done')


parser()