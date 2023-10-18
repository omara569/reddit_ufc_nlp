from transformers import XLNetTokenizer, XLNetForSequenceClassification
from typing import List, Tuple
from entity_recognition import extract_names, fuzzy_match_names
import torch
import torch.nn.functional as F
import pandas as pd
from structures.config import get_params
import os 


def ufc_fighter_list(names_path: str) -> List[str]:
    with open(names_path, 'r', encoding='utf-8') as f:
        individuals_list = [line.strip() for line in f.readlines()]
    return individuals_list


def load_data(parsed_posts_path: str) -> List[List[str]]:
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
            data.append([date, post])
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


def process_data(text_list: List[str], fighter_list: str, model, tokenizer) -> dict:
    fighter_list_dict = {fighter_name: {} for fighter_name in fighter_list} # We want a dictionary of our fighter_list with an array tracking each fighter's sentiment
    for post_text in text_list:
        post_info, comment_info = extract_content(post_text[1])
        # Break down a specific post further    
        specific_txt_list = [post_info['post_text']] # Contains all of our text from a given post. Each index is from a post/comment
        for comment_text in comment_info['comment_text']:
            specific_txt_list.append(comment_text)

        # Now we want to loop through the text and in each iteration we extract the names, fuzzy match with our list of fighters, and then perform the sentiment analysis on the text snippet in which they appear (i.e. the specific post or comment)
        entity_list = []
        for text in specific_txt_list:
            entities_recognized = extract_names(text)
            for entity in entities_recognized:
                best_match, _ = fuzzy_match_names(entity, fighter_list)
                entity_list.append(best_match)
            # Calculate the sentiments
            entity_sentiments = sentiment_calculation(text, model, tokenizer)
            for entity in entity_list:
                if entity:
                    if post_text[0] in fighter_list_dict[entity].keys():
                        fighter_list_dict[entity][post_text[0]].append(entity_sentiments)
                    else:
                        fighter_list_dict[entity][post_text[0]] = [entity_sentiments]

    return fighter_list_dict


def sentiment_calculation(input_text: str, model, tokenizer) -> torch.Tensor:
    inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = F.softmax(logits, dim=-1)
    return torch.argmax(probabilities, dim=1)


def sentiment_analysis():
    params = get_params()
    local_path = os.path.dirname(__file__) # Not used
    root_path = os.getcwd()
    
    # Get model and tokenizer
    print('Getting model and tokenizer')
    model_path = root_path + '/' + params.model_path
    model = XLNetForSequenceClassification.from_pretrained(model_path, num_labels=3) # ['Negative', 'Neurtral', 'Positive']
    tokenizer = XLNetTokenizer.from_pretrained(model_path)

    # Get list of UFC fighters
    print('Getting list of UFC fighters')
    fighter_names_path = root_path + '/' + params.fighter_names_path
    fighter_list = ufc_fighter_list(fighter_names_path)

    # Grab the data
    parsed_posts = root_path + '/' + params.posts_parsed
    data = load_data(parsed_posts) # Text data that we want to process

    # Sentiment Analysis on the data
    fighter_list_dict = process_data(data, fighter_list, model, tokenizer) # Looks at all posts one by one
    
    # From here, we need to keep track of each fighter and their overall sentiments at specific dating
    print('Adjusting information formatting')
    for fighter in fighter_list_dict.keys():
        for date in fighter_list_dict[fighter]:
            # Adjust the information in question to show the mean of the sentiment classifications gathered
            vals = torch.stack(fighter_list_dict[fighter][date])
            vals = vals.to(torch.float32)
            vals = torch.mean(vals)
            fighter_list_dict[fighter][date] = vals.item()
    
    print('Flattening Data')
    flattened_data = []
    for name, dates in fighter_list_dict.items():
        row = {'Fighter':name}
        row.update(dates)
        flattened_data.append(row)

    print('Saving Data Locally')
    save_name = local_path + '/output_data.xlsx'
    df = pd.DataFrame(flattened_data)
    df.to_excel(save_name, index=False) # Since there's no need to create an SQL server for now
    print('Done')


sentiment_analysis()