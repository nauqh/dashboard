import pandas as pd
from ast import literal_eval
import plotly.graph_objects as go


def graph_active_learners(df_merged):
    fig = go.Figure()

    # Add bar trace
    fig.add_trace(go.Bar(
        x=df_merged['number_of_threads'].head(10)[::-1],
        y=df_merged['name'].head(10)[::-1],
        orientation='h',
        text=df_merged['number_of_threads'].head(10)[::-1],
        marker_color="#1f77b4",
        hovertemplate='%{x} threads<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title='',
        xaxis=dict(title='Number of threads'),
        yaxis=dict(title='Learners'),
        hoverlabel=dict(bgcolor='#000', font_color='#fff'),
        margin=dict(t=30, l=0, r=0, b=30)
    )

    return fig


def graph_busy_hour(df_busy_hour):
    def calculate_average(start_index):
        return df_busy_hour.loc[start_index:start_index+6, 'number_of_threads'].mean()

    max_average = -1
    max_range = None

    # Iterate through the dataframe to find the range with the highest average
    for i in range(len(df_busy_hour) - 6):
        average = calculate_average(i)
        if average > max_average:
            max_average = average
            max_range = (i, i+6)
    x, y = max_range

    fig = go.Figure()

    # Add bar trace
    fig.add_trace(go.Bar(
        x=df_busy_hour['Hour'],
        y=df_busy_hour['number_of_threads'],
        text=df_busy_hour['number_of_threads'],
        textposition='outside',
        hovertemplate='%{x}h: %{y} threads<extra></extra>',
        marker=dict(color=['#FF4B4B' if df_busy_hour['Hour'][x] <= hour <=
                    df_busy_hour['Hour'][y] else '#1f77b4' for hour in df_busy_hour['Hour']])
    ))

    fig.add_annotation(
        x=0.58,
        y=0.8,
        xref='paper',
        yref='paper',
        text='Busiest hours',
        showarrow=False,
        font=dict(color='#ff7f0e', size=15)
    )

    fig.update_layout(
        title="",
        xaxis=dict(title='Hour'),
        yaxis=dict(title='Number of threads'),
        hoverlabel=dict(bgcolor='#000', font_color='#fff'),
        margin=dict(t=30, l=0, r=0, b=30)
    )
    fig.update_layout()
    fig.update_yaxes(showgrid=False)

    return fig


def graph_busy_day(df_busy_day, ascending):
    busiest_days = df_busy_day.sort_values(
        by='number_of_threads', ascending=ascending).head(2)['Day'].to_list()
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_busy_day['Day'],
        y=df_busy_day['number_of_threads'],
        text=df_busy_day['number_of_threads'],
        textposition='outside',
        marker=dict(color=['#FF4B4B' if hour in busiest_days
                    else '#1f77b4' for hour in df_busy_day['Day']]),
        hovertemplate='%{x}: %{y} threads<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title='',
        xaxis=dict(title=''),
        yaxis=dict(title='Number of threads'),
        hoverlabel=dict(bgcolor='#000', font_color='#fff'),
        margin=dict(t=30, l=0, r=0, b=30)
    )
    fig.update_yaxes(showgrid=False)

    return fig


def graph_popular_topics(df_merged):
    fig = go.Figure()

    # Add bar trace
    fig.add_trace(go.Bar(
        x=df_merged['number_of_threads'],
        y=df_merged['module'],
        text=df_merged['number_of_threads'],
        customdata=df_merged['name'],
        hovertemplate='Tag: #%{customdata}<extra></extra>',
        marker_color="#1f77b4",
        orientation='h'
    ))

    fig.update_layout(
        title='',
        xaxis=dict(title='Number of threads'),
        yaxis=dict(title='Topics'),
        hoverlabel=dict(bgcolor='#000', font_color='#fff'),
        margin=dict(t=30, l=0, r=0, b=30)
    )
    return fig
