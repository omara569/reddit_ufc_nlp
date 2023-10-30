from dataclasses import dataclass


@dataclass
class Params:
    reddit_page: str
    initial_run: bool
    days_prior: int
    gecko_driver_file_name: str
    reddit_posts_dir_name: str
    posts_parsed: str
    fighter_list_url: str
    fighter_names_path: str
    fighter_images_path: str
    bert_model: str
    model_path: str
    data_path: str


params_default = {
    'reddit_page': 'https://www.reddit.com/r/ufc/',
    'initial_run' : False,
    'days_prior' : 30, # How far back we want to collect data from (in days)
    'gecko_driver_file_name' : 'geckodriver.log',
    'reddit_posts_dir_name' : 'processing/reddit_posts',
    'posts_parsed':'processing/posts_parsed',
    'fighter_list_url': 'https://www.ufc.com/athletes/all',
    'fighter_names_path': '/processing/fighter_names.txt',
    'fighter_images_path': 'processing/fighter_images',
    'bert_model':'minh21/XLNet-Reddit-Sentiment-Analysis',
    'model_path': 'text_model',
    'data_path': 'sentiment_analysis/output_data.xlsx',
}


def get_params():
    return Params(**params_default) # args and kwargs