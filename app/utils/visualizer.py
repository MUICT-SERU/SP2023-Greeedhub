import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import json

COMPETENCY_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

def clean_for_json(obj):
    """Convert numpy/pandas objects to Python native types and handle NaN values."""
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (float, np.float64)):
        return float(obj) if not np.isnan(obj) else None
    elif isinstance(obj, (np.ndarray, pd.Series)):
        return [clean_for_json(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(x) for x in obj]
    return obj

def generate_visualizations(competency_data):
    """
    Generate visualizations to match the original Visualize_Code_Alive script:
    - Animated slider chart (bubble chart, animation by year)
    - Radar (spider) chart for each author
    """
    visualizations = []

    # Convert data to DataFrame
    author_stats = pd.DataFrame(competency_data['author_stats'])
    author_timeline = pd.DataFrame(competency_data['author_timeline'])

    # Merge competency_level into author_timeline
    if 'competency_level' in author_stats.columns:
        author_timeline = pd.merge(
            author_timeline,
            author_stats[['author_email', 'competency_level']],
            on='author_email',
            how='left'
        )

    # Ensure date columns are correct
    author_timeline['author_date'] = pd.to_datetime(author_timeline['author_date'])
    author_timeline['Year'] = author_timeline['author_date'].dt.year
    author_timeline['Month'] = author_timeline['author_date'].dt.month
    author_timeline['Level'] = author_timeline['competency_level']
    author_timeline['Value'] = author_timeline['hash']
    # Ensure Value is non-negative and greater than zero for bubble size
    author_timeline['Value'] = author_timeline['Value'].clip(lower=0.1)
    author_timeline['AuthorID'] = author_timeline['author_email']
    author_timeline['LevelOrder'] = author_timeline['Level'].map({level: i for i, level in enumerate(COMPETENCY_ORDER)})

    # Animated slider chart (bubble chart, animation by year)
    fig_slider = px.scatter(
        author_timeline,
        x='Month',
        y='LevelOrder',
        size='Value',
        color='Level',
        animation_frame='Year',
        range_x=[0.5, 12.5],
        range_y=[-0.5, len(COMPETENCY_ORDER)-0.5],
        labels={'LevelOrder': 'Competency Level', 'Value': 'Value'},
        hover_data={'AuthorID': True},
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_slider.update_layout(
        title="Overall Commits",
        height=420,
        margin=dict(l=30, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        xaxis=dict(tickmode='array', tickvals=list(range(1, 13)),
                   ticktext=['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December'],
                   gridcolor='#b0b3b8', linecolor='#1f2937', zerolinecolor='#b0b3b8', color='#1f2937'),
        yaxis=dict(tickmode='array', tickvals=list(range(len(COMPETENCY_ORDER))),
                   ticktext=COMPETENCY_ORDER,
                   gridcolor='#b0b3b8', linecolor='#1f2937', zerolinecolor='#b0b3b8', color='#1f2937'),
        paper_bgcolor='#fff',
        plot_bgcolor='#fff',
        font=dict(color='#1f2937', family='Inter, sans-serif')
    )
    if len(author_timeline['Value']) > 0:
        fig_slider.update_traces(marker=dict(sizemode='area', sizeref=2.5 * max(author_timeline['Value']) / (50 ** 2)))
    visualizations.append({
        'data': clean_for_json(fig_slider.to_dict()['data']),
        'layout': clean_for_json(fig_slider.to_dict()['layout'])
    })

    # Radar (spider) chart for each author
    author_totals = author_timeline.groupby('AuthorID')['Value'].sum().reset_index()
    radar_colors = px.colors.qualitative.Safe
    for i, author_id in enumerate(author_totals['AuthorID']):
        author_data = author_timeline[author_timeline['AuthorID'] == author_id]
        values = (author_data.groupby('Level')['Value'].sum() / author_totals.loc[author_totals['AuthorID'] == author_id, 'Value'].values[0] * 100).tolist()
        fig_spider = go.Figure()
        fig_spider.add_trace(go.Scatterpolar(
            r=values,
            theta=COMPETENCY_ORDER,
            fill='toself',
            name=author_id,
            line=dict(color=radar_colors[i % len(radar_colors)]),
            marker=dict(color=radar_colors[i % len(radar_colors)])
        ))
        fig_spider.update_layout(
            title=f"Developer Competency - AuthorID: {author_id}",
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#b0b3b8', linecolor='#1f2937', color='#1f2937')),
            paper_bgcolor='#fff',
            plot_bgcolor='#fff',
            font=dict(color='#1f2937', family='Inter, sans-serif')
        )
        visualizations.append({
            'data': clean_for_json(fig_spider.to_dict()['data']),
            'layout': clean_for_json(fig_spider.to_dict()['layout'])
        })

    return visualizations 