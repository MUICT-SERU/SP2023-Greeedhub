import os
import tempfile
from git import Repo
from pydriller import Repository
import pandas as pd
from pathlib import Path
import pytz

def analyze_repository(github_url):
    """
    Analyze a GitHub repository and extract commit data.
    
    Args:
        github_url (str): URL of the GitHub repository
        
    Returns:
        dict: Repository analysis data
    """
    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the repository
        repo_path = os.path.join(temp_dir, 'repo')
        Repo.clone_from(github_url, repo_path)
        
        # Initialize data collection
        commits_data = []
        
        # Analyze the repository using PyDriller
        for commit in Repository(repo_path).traverse_commits():
            # Convert timezone-aware dates to UTC
            author_date = commit.author_date.astimezone(pytz.UTC)
            committer_date = commit.committer_date.astimezone(pytz.UTC)
            
            commit_data = {
                'hash': commit.hash,
                'author_name': commit.author.name,
                'author_email': commit.author.email,
                'author_date': author_date,
                'committer_name': commit.committer.name,
                'committer_email': commit.committer.email,
                'committer_date': committer_date,
                'msg': commit.msg,
                'merge': commit.merge,
                'modified_files': [],
                'lines_added': 0,
                'lines_deleted': 0
            }
            
            # Analyze modified files
            for modified_file in commit.modified_files:
                file_data = {
                    'filename': modified_file.filename,
                    'change_type': modified_file.change_type.name,
                    'lines_added': modified_file.added_lines,
                    'lines_deleted': modified_file.deleted_lines,
                    'complexity': modified_file.complexity,
                    'nloc': modified_file.nloc,
                    'token_count': modified_file.token_count
                }
                commit_data['modified_files'].append(file_data)
                commit_data['lines_added'] += modified_file.added_lines
                commit_data['lines_deleted'] += modified_file.deleted_lines
            
            commits_data.append(commit_data)
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(commits_data)
        
        return {
            'commits': df.to_dict('records'),
            'repository_url': github_url,
            'total_commits': len(df),
            'total_authors': df['author_email'].nunique(),
            'date_range': {
                'start': df['author_date'].min().isoformat(),
                'end': df['author_date'].max().isoformat()
            }
        } 