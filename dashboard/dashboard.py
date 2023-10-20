import streamlit as st
import pandas as pd 
import numpy as np 
import altair as alt
from structures.config import get_params


@st.cache_data
def load_data(frame_path: str):
    data = pd.read_excel(frame_path)
    min_val = 0
    max_val = 2

    removed_col = data.pop('Fighter')
    normalized_data = 2 * (data - min_val) / (max_val - min_val) - 1
    normalized_data['Fighter'] = removed_col

    normalized_data = normalized_data.transpose()
    normalized_data = normalized_data.reset_index()
    normalized_data.columns = normalized_data.iloc[-1]
    normalized_data = normalized_data.drop(normalized_data.index[-1])
    normalized_data = normalized_data.rename(columns={'Fighter':'Date'})
    return normalized_data


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    


def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)


def search_fighter(search_query):
    data_load_state.text('Loading charts')
    # filtered_df = data[data['Fighter'].str.contains(search_query, case=False)]
    
    # filtered_df = data.filter(regex='|'.join([search_query, 'Date']))
    filtered_df = data[[col for col in data.columns if search_query.lower() in col.lower() or col=='Date']]
    if not filtered_df.empty:
        st.line_chart(filtered_df, x='Date')
    data_load_state.text('Input a Name in the text box below to look up fighter sentiments')
    


# config information
params = get_params()
local_css("dashboard/style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
# building out the app

# Initializations
st.title('UFC Fighter Sentiment History')
data_load_state = st.text('Loading data...')
data = load_data(params.data_path)
data_load_state.text('')
note = st.text('Note: Lower numbers indicate more negative sentiments')
note_2 = st.text('Higher numbers indicate more positive sentiments')

# Search bar
#icon("search")
search_bar = st.text_input("", "Islam Makhachev") # Shows sentiments over the past x days
if search_bar:
    search_fighter(search_bar)

# st.subheader('Raw data')
# st.write(data) # Writes table onto screen (interactive table!)

# Can do this instead if we want an interactable check box
# if st.checkbox('Show raw data'):
#     st.subheader('Raw data')
#     st.write(data)


# st.subheader('Sentiment histogram of values September 25th, 2023')
# hist_values = np.histogram(data['2023-09-25'], bins=24, range=(-1,4))[0]
# st.bar_chart(hist_values)

# st.map() # Used when we want to plot data on a map
# st.slider('hour', 0, 23, 17) # sets the min, max, and default values respectively in the 'hour' format

