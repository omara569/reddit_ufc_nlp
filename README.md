# reddit_ufc_nlp

UFC-NLP is an open-source project that gathers UFC fighter sentiments from the UFC reddit page.

The sentiment analysis is performed using HuggingFace transformers.

## Installation

It is recommended that a virual environment is used and the path to the directory containing these files is added to the path in the virtual environment.

These libraries and their dependencies can be installed using the "requirements.txt" file using [pip](https://pip.pypa.io/en/stable/installation/) package manager:
```bash
pip install requirements.txt
```

## HuggingFace model

To select the HuggingFace model, change the ```bert_model``` variable in the ```params_default``` dictionary to be the desired model. Though the variable name is "bert_model", is is not actually limited to BERT models, and is actually an XLNet model by default. Note that if an XLNet model is not being used, the following libraries must have their "transformers" imports adjusted:
- The "sentiment_analysis.py" file in the "sentiment_analysis" directory
- The "get_model.py" file in the "text_model" directory

## Updating the Dashboard Data

We run the following in this order:
```
python processing/scraper.py
python processing/parser.py
python sentiment_analysis/sentiment_analysis.py
```
Note that the "automate.bat" file already handles this if run from the command prompt in windows.

Other details on dashboard updates:
- It is recommended that the above snippets of code are run daily
- The scraper script will update the list of UFC fighters from the UFC page every Saturday
- If the initial run, change the "initial_run" variable in the "params_default" to be "True" and change it back to "False" afterward. This can be found in the config.py file in the structures directory 

## Running the dashboard

Streamlit is a dashboard framework used for the deployment of this project. It comes with a free community cloud for hosting dashboards straight from github repositories. Documentation can be found at [here](https://docs.streamlit.io/).

To run the dashboard locally, the following must be input into the command line:
streamlit run dashboard/published_dash.py

Note:
- There is another "structures" directory within the "dashboard" directory. This is due to the nature of streamlit - as it needs the "structures" directory to be local to the "published_dash.py" file in order to properly run on the cloud server. The "structures" directory is the same as the one in the root directory. 
- The "requirements.txt" file in the "dashboard" directory is for use by the streamlit cloud when hosting the dashboard.