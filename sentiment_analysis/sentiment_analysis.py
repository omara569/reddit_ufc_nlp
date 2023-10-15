from transformers import BertTokenizer, BertModel, BertForSequenceClassification
from typing import List, Any, Tuple
from entity_recognition import extract_names
import pandas as pd
from structures.config import get_params
import os 


def ufc_fighter_list(names_path: str) -> List[str]:
    with open(names_path, 'r', encoding='utf-8') as f:
        individuals_list = [line.strip() for line in f.readlines()]
    return individuals_list


def load_data(parsed_posts_path: str) -> List[str]:
    dates_dir = os.listdir(parsed_posts_path)
    data = []
    for date in dates_dir:
        sub_path = parsed_posts_path + '/' + date
        post_dir = os.listdir(sub_path) # The individual posts in question
        for post in post_dir:
            # Path to the text file for the post. This text file contains all the text from the comments and post. Also contains the user and timestamp of each post
            final_path = sub_path + '/' + post + '/' + 'text.txt' 
            with open(final_path, mode='r', encoding='utf-8') as f:
                post = f.read()
            data.append(post)
    return data


def extract_content(text: str) -> Tuple[dict]:
    splitted = text.split('\n')
    indices = []
    for idx, text in enumerate(splitted):
        if 'posted at' in text or 'replied at' in text:
            indices.append(idx)
    
    # Further parsing the post text to extract the content
    post = ''
    comments = []
    for idx_indices, val in enumerate(indices):
        if idx_indices==0 and len(indices) > 1:
            post = ' '.join( splitted[idx_indices:indices[idx_indices+1]] )
        elif len(indices) == 1:
            post = ' '.join(splitted)
        elif val != indices[-1]:
            comment = ' '.join( splitted[val: indices[idx_indices+1]] )
            comments.append(comment)
        else:
            comment = ' '.join( splitted[val:] )

    post_splitted = post.split(' posted at ')
    post_info = {'poster': post_splitted[0].strip(' '), 'post_time': post_splitted[1].split(': ')[0], 'post_text': post_splitted[1].split(': ')[1].strip(' ')}
    comment_info = {'commenter':[], 'comment_time':[], 'comment_text':[]}
    for comment in comments:
        comment_splitted = comment.split(' replied at ')
        comment_info['commenter'].append(comment_splitted[0].strip(' '))
        comment_info['comment_time'].append(comment_splitted[1].split(': ')[0])
        comment_info['comment_text'].append(comment_splitted[1].split(': ')[1].strip(' '))
    return post_info, comment_info


def process_data(text_list: List[str]):
    for post_text in text_list:
        post_info, comment_info = extract_content(post_text)
    
    txt_list = [post_info['post_text']] # Contains all of our text from a given post. Each index is from a post/comment
    for comment_text in comment_info['comment_text']:
        txt_list.append(comment_text)
    # Now we want to loop through the text and in each iteration we extract the names, fuzzy match with our list of fighters, and then perform the sentiment analysis on the text snippet in which they appear (i.e. the specific post or comment)
    # TODO: Pick up from here


def sentiment_analysis():
    params = get_params()
    local_path = os.path.dirname(__file__)
    root_path = os.getcwd()
    
    # Get model and tokenizer
    print('Getting model and tokenizer')
    model_path = root_path + '/' + params.model_path
    model = BertModel.from_pretrained(model_path)
    tokenizer = BertTokenizer.from_pretrained(model_path)

    # Get list of UFC fighters
    print('Getting list of UFC fighters')
    fighter_names_path = root_path + '/' + params.fighter_names_path
    fighter_list = ufc_fighter_list(fighter_names_path)

    # Grab the data
    parsed_posts = root_path + '/' + params.posts_parsed
    data = load_data(parsed_posts)
    # TODO: Pick up from here
    process_data(data)
    print('Done')


sentiment_analysis()