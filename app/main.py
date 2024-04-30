import streamlit as st
import streamlit_shadcn_ui as ui

import pandas as pd
from ast import literal_eval
from graph import *

st.set_page_config(
    page_title="Dashboard",
    page_icon="data/favicon.png",
    layout="wide")

st.title("📑Discord question-center April Recap")
st.markdown("_Prototype v1.0.0_")


@st.cache_data
def load_data():
    df = pd.read_csv("data/threads.csv",
                     parse_dates=['created_at'],
                     converters={'tags': literal_eval, 'messages': literal_eval})
    users = pd.read_csv("data/users.csv",
                        converters={'roles': literal_eval})
    tags = pd.read_csv("data/tags.csv")
    return df, users, tags


df, users, df_tag = load_data()

st.write("##")
cols = st.columns(3)
with cols[0]:
    ui.metric_card(title="Total Threads",
                   content=len(df), key="card1")
with cols[1]:
    ui.metric_card(title="Learners Posted Questions",
                   content=df['author_id'].nunique(), key="card2")
with cols[2]:
    df_learner = users[(users['roles'].apply(len) == 2) & (
        users['roles'].apply(lambda x: 957854915194126339 in x))]
    ui.metric_card(title="Total Learners",
                   content=len(df_learner), key="card3")


# NOTE: ACTIVE LEARNER
# Count threads by user
df_thread_counts = df['author_id'].value_counts().rename_axis(
    'id').reset_index(name='number_of_threads')
df_merged = pd.merge(df_thread_counts, df_learner, how="left", on='id')

fig = graph_active_learners(df_merged)

st.write("##")
st.subheader("Most active learners")
cols = st.columns([1, 3])
with cols[0]:
    st.write("##")
    st.write("**⚠️Problem**: Cannot calculate percentage of learner posting questions since every Discord member has `#learner` tag as default.")
    st.write("I tried to find users that have only one `#learner` role but still not accurate since there are learners that have completed the course but still stay in Discord.")
    st.write("""**✅Solution**:
  - Get active learners from google sheet's learner master list
  - Assign `new_role`(hidden) and filter only active learner using that role""")
with cols[1]:
    st.plotly_chart(fig, use_container_width=True)


# NOTE: BUSIEST HOUR
# Extract day of week and hour
df['Day'] = df['created_at'].dt.day_name()
df['Hour'] = df['created_at'].dt.hour

# Count threads by day and hour
df_busy_day = df.groupby(['Day']).agg({'id': 'count'}).reset_index().rename(
    columns={'id': 'number_of_threads'})
df_busy_hour = df.groupby(['Hour']).agg(
    {'id': 'count'}).reset_index().rename(columns={'id': 'number_of_threads'})
df_busy_hour['Hour'] = (df_busy_hour['Hour'] + 8) % 24
fig_busy_hour, metric2 = graph_busy_hour(df_busy_hour)

# NOTE: BUSIEST DAY
# Convert the 'Day' column to a categorical type with the specified order
df_busy_day['Day'] = pd.Categorical(df_busy_day['Day'],
                                    categories=[
                                        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                                    ordered=True)

# Sort the DataFrame by the 'Day' column
df_busy_day = df_busy_day.sort_values(by='Day')

st.write("##")
st.subheader("Time learners post the most questions")
cols = st.columns([1, 3.5])
with cols[0]:
    ui.metric_card(title="Total TAs",
                   content=6, description="+2 TAs from last month", key="card4")
    ui.metric_card(title="Threads In Busiest Hour",
                   content=float(metric2),
                   description=f"{metric2*100/len(df):.2f}% of total threads",
                   key="card5")
    ui.metric_card(title="Total Threads",
                   content=len(df), key="card6")
with cols[1]:
    st.plotly_chart(fig_busy_hour, use_container_width=True)

st.write("##")
cols = st.columns([1, 1])
with cols[0]:
    st.subheader("Busiest day")
    option = ui.tabs(options=['Busiest', 'Least busy'],
                     default_value='Busiest')
    ascending = True if option == 'Least busy' else False
    fig = graph_busy_day(df_busy_day, ascending)
    st.plotly_chart(fig, use_container_width=True)
with cols[1]:
    # NOTE: MOST ASKED MODULE
    df_tag_counts = df.explode('tags')['tags'].value_counts(
    ).rename_axis('id').reset_index(name='number_of_threads')
    # Dictionary for module names
    module_names = {
        'M1.1': 'SQL Basics',
        'M1.2': 'SQL Advanced',
        'M2.1': 'Python 101',
        'M3.1': 'Pandas basics',
        'M3.2': 'Prepare your data',
        'M4': 'Data visualization'
    }
    df_merged = pd.merge(df_tag_counts, df_tag, how="left", on='id')
    df_merged = df_merged.dropna(subset=['name']).reset_index(drop=True)
    df_merged['module'] = df_merged['name'].apply(
        lambda x: module_names.get(x, x))

    fig = graph_topics2(df_merged[:7])
    st.subheader("Most asked topics")
    st.plotly_chart(fig, use_container_width=True)


# NOTE: RESPONSE TIME
df['response'] = pd.to_datetime(
    df['messages'].apply(lambda x: x[-2]['created_at']))
df['response_time'] = df['response'] - df['created_at']


st.write("##")

st.subheader("Response time")
fig = graph_response_time(df)
st.plotly_chart(fig, use_container_width=True)

st.write("""
**NOTE**: Response time is determined by subtracting the initial reply message from the time the thread was created

    response_time = time_of_first_reply - created_time_of_thread

For threads that have delayed response:
- Some threads were posted after 10pm -> responded the next day
- After posting thread on forum, learner contact TA directly for solution. Solved in group chat.
- TA sessions are full on Wednesday and Friday morning shift -> some threads were responded late on those days (longest: 4 hours 18/4)""")

st.write("""
**NOTE**: Calculate time until resolved

    resolve_time = time_of_last_reply - created_time_of_thread

**⚠️Problem**: There are threads that are refered back by TAs to solve similar queries. TA tag learner in old similar threads that has been solved -> `time_of_last_reply` is not accurate.

**✅Solution**: Remove thread that has `resolve_time` more than a day.
         """)
