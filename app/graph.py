import plotly.graph_objects as go
import pandas as pd


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
        y=1,
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
        margin=dict(t=0, l=0, r=0, b=0)
    )
    fig.update_layout()
    fig.update_yaxes(showgrid=False)

    return fig, df_busy_hour[x:y+1]['number_of_threads'].sum()


def graph_busy_day(df_busy_day, ascending):
    df_busy_day['Day'] = df_busy_day['Day'].apply(lambda x: x[:3])
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
        margin=dict(t=0, l=0, r=0, b=0)
    )
    fig.update_yaxes(showgrid=False)

    return fig


def graph_busy_day2(df_april, df_may):
    # Extract day and hour from 'created_at' column
    df_april['Day'] = df_april['created_at'].dt.day_name()
    df_may['Day'] = df_may['created_at'].dt.day_name()

    # Count threads by day for April and May
    df_busy_day_april = df_april.groupby(['Day']).agg(
        {'id': 'count'}).reset_index().rename(columns={'id': 'number_of_threads_april'})
    df_busy_day_may = df_may.groupby(['Day']).agg(
        {'id': 'count'}).reset_index().rename(columns={'id': 'number_of_threads_may'})

    # Merge the data frames
    df_busy_day = pd.merge(df_busy_day_april, df_busy_day_may,
                           on='Day', how='outer').fillna(0)

    # Convert the 'Day' column to a categorical type with the specified order
    df_busy_day['Day'] = pd.Categorical(df_busy_day['Day'],
                                        categories=[
                                            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                                        ordered=True)

    # Sort the DataFrame by the 'Day' column
    df_busy_day = df_busy_day.sort_values(by='Day')

    # Create a grouped bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_busy_day['Day'],
        y=df_busy_day['number_of_threads_april'],
        name='April',
        text=df_busy_day['number_of_threads_april'],
        textposition='outside',
        hovertemplate='%{x} April: %{y} threads<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_busy_day['Day'],
        y=df_busy_day['number_of_threads_may'],
        name='May',
        text=df_busy_day['number_of_threads_may'],
        textposition='outside',
        hovertemplate='%{x} May: %{y} threads<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        barmode='group',
        title='',
        xaxis=dict(title=''),
        yaxis=dict(title='Number of threads'),
        hoverlabel=dict(bgcolor='#000', font_color='#fff'),
        margin=dict(t=0, l=0, r=0, b=0),
        legend=dict(
            orientation="h",
            y=1,
            x=0.5
        )
    )
    fig.update_yaxes(showgrid=False)

    return fig


def graph_response_time(df):
    df['response'] = pd.to_datetime(
        df['messages'].apply(lambda x: x[-2]['created_at']))
    df['response_time'] = df['response'] - df['created_at']
    fig = go.Figure(data=go.Scatter(
        x=df.index,
        y=df['response_time'][::-1].dt.total_seconds() / 60,
        mode='lines',
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
    return fig


def graph_topics(df, df_tag):
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
    df_merged = df_merged[:7]

    decades = df_merged['module']
    counts = df_merged['number_of_threads']
    colors = ['#b9fbc0', '#98f5e1', '#8eecf5',
              '#90dbf4', '#a3c4f3', '#cfbaf0', 'f1c0e8']

    fig = go.Figure(data=[go.Pie(labels=decades, values=counts, hole=0.4, sort=False,
                                 direction='clockwise', pull=[0.1]*len(decades))])

    fig.update_traces(name='', textinfo='none',
                      hovertemplate='Module: %{label}<br>Threads: %{value}',
                      marker=dict(colors=colors, line=dict(color='#000', width=1)))

    fig.update_layout(
        margin=dict(t=0, l=0, r=0),
        hoverlabel=dict(bgcolor='#000', font_color='#fff'),
        legend=dict(
            orientation="h",
            y=-0.1,
            x=0.1
        )
    )

    return fig
