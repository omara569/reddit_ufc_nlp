from transformers import BertTokenizer, BertModel
from structures.config import get_params
import os


def save_model():
    params = get_params() # Params
    local_path = os.path.dirname(__file__) # Returns the working directory of this script

    model_name = params.bert_model # Pre-trained model variation we're selecting
    model = BertModel.from_pretrained(model_name)
    tokenizer = BertTokenizer.from_pretrained(model_name)

    model.save_pretrained(local_path)
    tokenizer.save_pretrained(local_path)


save_model()