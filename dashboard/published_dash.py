import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt
from typing import List, Tuple
import altair as alt
from fuzzywuzzy import fuzz
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


def search_fighter(search_bar) -> str:
    if search_bar is not None:
        best_match, _ = fuzzy_match_names(search_bar, fighter_names)
        if best_match is None:
            best_match = "Islam Makhachev".upper()
        #filtered_df = data[[col for col in data.columns if search_query.lower() in col.lower() or col=='Date']]
        filtered_df = data[[best_match, 'Date']]
        filtered_df[best_match] = filtered_df[best_match].interpolate() # interpolate missing points
        filtered_df[best_match] = filtered_df[best_match].fillna(0) # Leftover points are zeros
        filtered_df['color'] = filtered_df[best_match].map(lambda x: 'green' if x > 0 else 'red' if x < 0 else 'black')
        # Create chart        
        chart = alt.Chart(filtered_df).mark_circle(size=100).encode(
            x='Date',  # Ordinal encoding for discrete x-axis
            y=best_match,  # Quantitative encoding for y-axis
            color=alt.Color('color:N', scale=None)
        )
        # Add thin bars using rule mark
        bars = alt.Chart(filtered_df).mark_rule(strokeWidth=2).encode(
            x='Date',
            y=best_match,
            color=alt.Color('color:N', scale=None)
        )
        # Combine the chart and bars
        combined_chart = chart + bars
        combined_chart = combined_chart.properties( 
            width=700,
            height=300
        )
        # Customize the appearance
        combined_chart = combined_chart.configure_view(
            stroke='transparent'  # Remove axis strokes for cleaner appearance
        )
        st.altair_chart(combined_chart)
    return best_match


def get_fighter_names(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as f:
        individuals_list = [line.strip() for line in f.readlines()]
    return individuals_list


def fuzzy_match_names(name: str, individual_list: List[str], threshold=50) -> Tuple:
    best_match = None
    best_score = 0
    for individual in individual_list:
        score = fuzz.token_set_ratio(name, individual)
        if score > threshold and score > best_score:
            best_match = individual
            best_score = score 
    return best_match, best_score


def fighter_hist(best_match):
    filtered_df = data[best_match]
    filtered_df = filtered_df.interpolate().fillna(0)
    filtered_df = pd.DataFrame(filtered_df)
    histogram = alt.Chart(filtered_df).mark_bar().encode( 
        x=alt.X(best_match, bin=alt.Bin(maxbins=30)),
        y='count()'
    ).properties(
        width=700,
        height=400
    )
    st.altair_chart(histogram)


def bubble():
    avged_data = data[[col for col in data.columns if col!='Date']]
    avged_data = avged_data.fillna(0)
    avged_data = avged_data.mean(axis=0)
    avged_data = pd.DataFrame(avged_data)
    avged_data = avged_data.reset_index()
    avged_data.columns = ['Fighter', 'Sentiment Value']
    avged_data = avged_data.sort_values(by='Sentiment Value', ascending=True)
    avged_data['Delta from Next'] = avged_data['Sentiment Value'].diff()
    most_positive = avged_data.tail(n=5)
    most_negative = avged_data.head(n=5)
    most_positive['color'] = 'green'
    most_negative['color'] = 'red'
    most_negative['Delta from Next'].iloc[0] = 0
    st.write('Top 5 Most positively and negatively talked about fighters')
    chart = alt.Chart(data=most_positive).mark_circle().encode( 
        x='Fighter',
        y='Sentiment Value',
        size = 'Delta from Next',
        color = alt.Color('color:N', scale=None)
    )
    chart_2 = alt.Chart(data=most_negative).mark_circle().encode( 
        x='Fighter',
        y='Sentiment Value',
        size='Delta from Next', 
        color = alt.Color('color:N', scale=None)
    )
    chart_out = chart+chart_2
    chart_out = chart_out.properties(
        width=700,
        height=400
    ).configure_legend(disable=True)
    st.altair_chart(chart_out)    


# config information
params = get_params()
local_css("dashboard/style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

## BUILDING OUT THE APP
# Credit where it's due:
# Define the content
content = """
<div style="position: fixed; top: 50px; left: 10px;">
    <p>Developed by Omar Abu-Hijleh</p>
    <p>Github: <a href="https://github.com/omara569/reddit_ufc_nlp/tree/main" target="_blank">https://github.com/omara569/reddit_ufc_nlp/tree/main</a></p>
    <p>LinkedIn: <a href="https://www.linkedin.com/in/omar-abu-hijleh/" target="_blank">https://www.linkedin.com/in/omar-abu-hijleh/</a></p>
</div>
"""
st.markdown(content, unsafe_allow_html=True)

# Initializations
st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <h1>UFC Fighter Sentiment History</h1>
    </div>
    """,
    unsafe_allow_html=True
)

fighter_names = get_fighter_names(params.fighter_names_path[1:])
data = load_data(params.data_path)
data_load_state = st.write('Input a Name in the text box below to look up fighter sentiments')
note = st.text('Note: Lower numbers indicate more negative sentiments')
note_2 = st.text('Higher numbers indicate more positive sentiments')

# Search bar
search_bar = st.text_input("", "Islam Makhachev") # Shows sentiments over the past x days
best_match = search_fighter(search_bar)
st.write('Showing data for ' + best_match)
fighter_hist(best_match)

bubble()
