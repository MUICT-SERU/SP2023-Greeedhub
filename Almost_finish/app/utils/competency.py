import pandas as pd
import numpy as np
from datetime import datetime
import pytz

def calculate_competency(repo_data):
    """
    Calculate competency scores from repository data.
    
    Args:
        repo_data (dict): Repository analysis data from git_analyzer
        
    Returns:
        dict: Competency analysis results
    """
    # Convert commits data back to DataFrame
    df = pd.DataFrame(repo_data['commits'])
    
    # Convert timezone-aware datetime to UTC
    df['author_date'] = pd.to_datetime(df['author_date']).dt.tz_localize(None)
    df['committer_date'] = pd.to_datetime(df['committer_date']).dt.tz_localize(None)
    
    # Calculate basic metrics
    df['commit_size'] = df['lines_added'] + df['lines_deleted']
    df['commit_complexity'] = df['modified_files'].apply(
        lambda x: sum(f['complexity'] for f in x if f['complexity'] is not None)
    )
    
    # Group by author
    author_stats = df.groupby('author_email').agg({
        'hash': 'count',  # number of commits
        'commit_size': ['mean', 'std', 'sum'],
        'commit_complexity': ['mean', 'std', 'sum'],
        'lines_added': 'sum',
        'lines_deleted': 'sum'
    }).reset_index()
    
    # Flatten column names
    author_stats.columns = ['_'.join(col).strip('_') for col in author_stats.columns.values]
    
    # Calculate competency levels (A1-C2) based on metrics
    def calculate_level(row):
        # Normalize metrics
        commits = row['hash_count']
        avg_size = row['commit_size_mean']
        avg_complexity = row['commit_complexity_mean']
        total_changes = row['lines_added_sum'] + row['lines_deleted_sum']
        
        # Define thresholds for each level
        if commits < 5 or total_changes < 100:
            return 'A1'
        elif commits < 10 or total_changes < 500:
            return 'A2'
        elif commits < 20 or total_changes < 2000:
            return 'B1'
        elif commits < 50 or total_changes < 5000:
            return 'B2'
        elif commits < 100 or total_changes < 10000:
            return 'C1'
        else:
            return 'C2'
    
    author_stats['competency_level'] = author_stats.apply(calculate_level, axis=1)
    
    # Calculate time-based metrics
    author_timeline = df.groupby(['author_email', pd.Grouper(key='author_date', freq='M')]).agg({
        'hash': 'count',
        'commit_size': 'sum',
        'commit_complexity': 'sum'
    }).reset_index()
    
    return {
        'author_stats': author_stats.to_dict('records'),
        'author_timeline': author_timeline.to_dict('records'),
        'repository_url': repo_data['repository_url'],
        'analysis_date': datetime.now(pytz.UTC).isoformat(),
        'total_commits': repo_data['total_commits'],
        'total_authors': repo_data['total_authors'],
        'date_range': {
            'start': df['author_date'].min().isoformat(),
            'end': df['author_date'].max().isoformat()
        }
    } 