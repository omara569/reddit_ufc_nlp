import spacy
from fuzzywuzzy import fuzz
from typing import List, Tuple

def extract_names(text: str) -> str:
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    names = []
    for ent in doc.ents:
        names.append(ent.text)
    return names


def fuzzy_match_names(name: str, individual_list: List[str], threshold=50) -> Tuple:
    best_match = None
    best_score = 0
    for individual in individual_list:
        score = fuzz.token_set_ratio(name, individual)

        if score > threshold and score > best_score:
            best_match = individual
            best_score = score 
    return best_match, best_score