from dataclasses import dataclass


@dataclass
class Params:
    reddit_page: str
    initial_run: bool


params_default = {
    'reddit_page': 'https://www.reddit.com/r/ufc/',
    'initial_run' : True
}


def get_params():
    return Params(**params_default) # args and kwargs