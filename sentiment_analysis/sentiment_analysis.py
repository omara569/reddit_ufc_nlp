from transformers import BertTokenizer, BertModel, BertForSequenceClassification
from typing import List, Any
from structures.config import get_params
import os 


def ufc_fighter_list(names_path: str) -> List[str]:
    with open(names_path, 'r', encoding='utf-8') as f:
        individuals_list = [line.strip() for line in f.readlines()]
    return individuals_list


def preprocess_data(fighter_list: List[str], parsed_posts_path: str):
    dates_dir = os.listdir(parsed_posts_path)
    for date in dates_dir:
        sub_path = parsed_posts_path + '/' + date
        post_dir = os.listdir(sub_path) # The individual posts in question
        for post in post_dir:
            # Path to the text file for the post. This text file contains all the text from the comments and post. Also contains the user and timestamp of each post
            final_path = sub_path + '/' + post + '/' + 'text.txt' 
            with open(final_path, mode='r', encoding='utf-8') as f:
                post = f.read()
            # Now break the post down
                    


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

    # Preprocess the text data from each post
    parsed_posts = root_path + '/' + params.posts_parsed
    preprocess_data(fighter_list, parsed_posts)

    print('Done')


sentiment_analysis()