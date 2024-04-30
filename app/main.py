import sqlite3
import streamlit as st
import streamlit_shadcn_ui as ui

import pandas as pd
from ast import literal_eval
from graph import *
import plotly.graph_objects as go


st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide")

st.title("📑Discord question-center April Recap")

# NOTE: Connect db and read data
df = pd.read_csv("data/threads.csv",
                 parse_dates=['created_at'],
                 converters={'tags': literal_eval, 'messages': literal_eval})
conn = sqlite3.connect('data/teo.db')

st.write("##")
cols = st.columns(3)
with cols[0]:
    ui.metric_card(title="Total Threads",
                   content=len(df), key="card1")
with cols[1]:

    ui.metric_card(title="Learners Posted Questions",
                   content=df['author_id'].nunique(), key="card2")
with cols[2]:
    query = """
-- Learners are users with one role and that role is #learner
WITH
    users_with_only_learner_role AS (
        SELECT
            user_id,
            role_id
        FROM
            user_role
        WHERE
            role_id = 957854915194126339
        GROUP BY
            user_id
        HAVING
            COUNT(role_id) = 1
    )
SELECT
    u.user_id,
    users.name
FROM
    users_with_only_learner_role u
    JOIN users ON u.user_id = users.id
WHERE
    users.name IS NOT NULL;
"""
    ui.metric_card(title="Total Learners",
                   content=len(pd.read_sql_query(query, conn)), key="card3")


# NOTE: ACTIVE LEARNER
# Get all users from database
df_user = pd.read_sql_query("select * from users", conn)
# Count threads by user
df_thread_counts = df['author_id'].value_counts().rename_axis(
    'id').reset_index(name='number_of_threads')
df_merged = pd.merge(df_thread_counts, df_user, how="left", on='id')


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

fig = graph_busy_hour(df_busy_hour)
st.plotly_chart(fig, use_container_width=True)

st.write("##")
cols = st.columns([1, 1.5])
with cols[0]:
    st.subheader("Busiest day")
    option = ui.tabs(options=['Busiest', 'Least busy'],
                     default_value='Busiest')
    ascending = True if option == 'Least busy' else False
    fig = graph_busy_day(df_busy_day, ascending)
    st.plotly_chart(fig, use_container_width=True)
with cols[1]:
    # NOTE: MOST ASKED MODULE
    df_tag = pd.read_sql_query("select * from tags", conn)
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

    fig = graph_popular_topics(df_merged)

    st.subheader("Most asked topics")
    st.write("##")
    st.plotly_chart(fig, use_container_width=True)

# NOTE: RESPONSE TIME
df['response'] = pd.to_datetime(
    df['messages'].apply(lambda x: x[-2]['created_at']))
df['response_time'] = df['response'] - df['created_at']

fig = go.Figure(data=go.Scatter(x=df.index,
                                y=df['response_time'][::-
                                                      1].dt.total_seconds() / 60,
                                mode='lines+markers',
                                text=df['created_at'][::-1].dt.date,
                                hovertemplate='Posted on %{text}<extra></extra>'
                                ))

fig.update_layout(
    title='',
    yaxis_title='Response Time (minutes)',
    margin=dict(t=30, l=0, r=0, b=30),
    hoverlabel=dict(bgcolor='#000', font_color='#fff')
)

fig.update_xaxes(title='Threads', showticklabels=False)
fig.update_yaxes(showgrid=False)

fig.add_shape(type="line",
              x0=df.index.min(), y0=200,
              x1=df.index.max(), y1=200,
              line=dict(color="red", width=2))
fig.add_annotation(x=df.index.min(), y=230,
                   text="3 hours",
                   showarrow=False,
                   font_color="red",
                   font_size=15)

st.write("##")
st.subheader("Response time")
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
