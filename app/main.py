import streamlit as st
import streamlit_shadcn_ui as ui

import pandas as pd
from ast import literal_eval
from graph import *

st.set_page_config(
    page_title="Dashboard",
    page_icon="data/favicon.png",
    layout="wide"
)

# with st.sidebar:
#     course = st.selectbox(
#         'Select course',
#         ('Data Science', 'Data Analysis Express', 'Fullstack Development'))

st.title(f"📑Discord question-center May Recap")
st.markdown("_Prototype v0.0.12_")


@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/threads.csv",
        parse_dates=['created_at'],
        converters={'tags': literal_eval,
                    'messages': literal_eval}
    )
    users = pd.read_csv("data/members_data.csv",
                        converters={'roles': literal_eval})
    tags = pd.read_csv("data/tags.csv")
    return df, users, tags


df, users, df_tag = load_data()
df_april = df[df['created_at'].dt.month == 4]
df_may = df[df['created_at'].dt.month == 5]

st.write("##")
cols = st.columns(3)
with cols[0]:
    with st.container(border=True):
        st.metric(
            label="Total Threads",
            value=len(df_may),
            delta=f"{(len(df_may) - len(df_april))/len(df_april)*100:.1f}% than last month"
        )
with cols[1]:
    with st.container(border=True):
        nunique_april = df_april['author_id'].nunique()
        nunique_may = df_may['author_id'].nunique()
        st.metric(
            label="Learners Posted Questions",
            value=df_may['author_id'].nunique(),
            delta=f"{(nunique_april - nunique_may)/nunique_april*100:.1f}% than last month",
        )
with cols[2]:
    df_learner = users[(users['roles'].apply(len) == 2) & (
        users['roles'].apply(lambda x: 957854915194126339 in x))]
    with st.container(border=True):
        st.metric(
            label="Total Learners",
            value=len(df_learner),
            delta="To be updated",
            delta_color="off"
        )

# NOTE: ACTIVE LEARNER
# Count threads by user
# df_thread_counts = df['author_id'].value_counts().rename_axis(
#     'id').reset_index(name='number_of_threads')
# df_merged = pd.merge(df_thread_counts, df_learner, how="left", on='id')


with st.container(border=True):
    st.subheader("Most active learners")
    option = ui.tabs(options=['April', 'May'],
                     default_value='May')
    df_to_graph = df_may if option == 'May' else df_april
    df_thread_counts = df_to_graph['author_id'].value_counts().rename_axis(
        'id').reset_index(name='number_of_threads')
    df_merged = pd.merge(df_thread_counts, df_learner, how="left", on='id')

    fig = graph_active_learners(df_merged)
    st.plotly_chart(fig, use_container_width=True)

# NOTE: BUSIEST HOUR
# Extract day of week and hour
df['Hour'] = df['created_at'].dt.hour

# Count threads by hour
df_busy_hour = df.groupby(['Hour']).agg(
    {'id': 'count'}).reset_index().rename(columns={'id': 'number_of_threads'})
df_busy_hour['Hour'] = (df_busy_hour['Hour'] + 8) % 24
fig_busy_hour, metric2 = graph_busy_hour(df_busy_hour)

cols = st.columns([1, 3.5])
with cols[0]:
    with st.container(border=True):
        st.metric(label="Total TAs",
                  value=8, delta="+2 TAs from last month",
                  delta_color="off")
    with st.container(border=True):
        st.metric(label="**Threads In Busiest Hour**",
                  value=metric2, delta=f"{metric2*100/len(df):.2f}% of total threads",
                  delta_color="off")
    with st.container(border=True):
        st.metric(label="**Threads In Busiest Day**",
                  value=32, delta=f"{32*100/len(df):.2f}% of total threads",
                  delta_color="off")

with cols[1]:
    with st.container(border=True):
        st.subheader("Time learners post the most questions")
        st.plotly_chart(fig_busy_hour, use_container_width=True)

cols = st.columns([1.5, 1])
with cols[0]:
    with st.container(border=True):
        st.subheader("Busiest day")
        fig = graph_busy_day2(df_april, df_may)
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
    with st.container(border=True):
        fig = graph_topics2(df_merged[:7])
        st.subheader("Most asked topics")
        st.plotly_chart(fig, use_container_width=True)

# NOTE: RESPONSE TIME
df['response'] = pd.to_datetime(
    df['messages'].apply(lambda x: x[-2]['created_at']))
df['response_time'] = df['response'] - df['created_at']

with st.container(border=True):
    st.subheader("Response time")
    fig = graph_response_time(df)
    st.plotly_chart(fig, use_container_width=True)

st.write("##")
st.subheader("Problem address")

with st.container(border=True):
    st.write("**⚠️Problem**: Cannot calculate percentage of learner posting questions since every Discord member has `#learner` tag as default.")
    st.write("I tried to find users that have only one `#learner` role but still not accurate since there are learners that have completed the course but still stay in Discord.")
    st.write("""**✅Solution**:                 
    - Get active learners from google sheet's learner master list
    - Assign `new_role`(hidden) and filter only active learner using that role""")

with st.container(border=True):
    st.write("""
    **NOTE**: Response time is determined by subtracting the initial reply message from the time the thread was created

        response_time = time_of_first_reply - created_time_of_thread

    For threads that have delayed response:
    - Some threads were posted after 10pm -> responded the next day
    - After posting thread on forum, learner contact TA directly for solution. Solved in group chat.
    - TA sessions are full on Wednesday and Friday morning shift -> some threads were responded late on those days (longest: 4 hours 18/4)""")

with st.container(border=True):
    st.write("""
    **NOTE**: Calculate time until resolved

        resolve_time = time_of_last_reply - created_time_of_thread

    **⚠️Problem**: There are threads that are refered back by TAs to solve similar queries. TA tag learner in old similar threads that has been solved -> `time_of_last_reply` is not accurate.

    **✅Solution**: Remove thread that has `resolve_time` more than a day.
            """)
