from dataclasses import dataclass


@dataclass
class Params:
    reddit_page: str
    initial_run: bool
    days_prior: int


params_default = {
    'reddit_page': 'https://www.reddit.com/r/ufc/',
    'initial_run' : True,
    'days_prior' : 1, # How far back we want to collect data from (in days)
}


def get_params():
    return Params(**params_default) # args and kwargs