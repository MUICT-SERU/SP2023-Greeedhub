import pandas as pd
import os
import json
from collections import defaultdict

# Load the CSV file
file_path = 'C:/Users/rujip/Desktop/SP2023-Greeedhub/pycefr/data.csv'  # Update this to your actual file path
data = pd.read_csv(file_path)

# Function to parse the file name and extract components
def parse_filename(file_name):
    parts = file_name.split('_')
    commit_hash = parts[0]
    project_name = parts[1]
    author_id = parts[2]
    author_date = parts[3]
    author_time = parts[4]
    commit_type = parts[5]  # "after" or "before"
    return commit_hash, project_name, author_id, author_date, author_time, commit_type

# Dictionary for scores
scores_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

# Process each row in the DataFrame
for index, row in data.iterrows():
    commit_hash, project_name, author_id, author_date, author_time, commit_type = parse_filename(row['File Name'])
    level = row['Level']
    displacement = row['Displacement']
    
    # Update scores
    scores_dict[(commit_hash, project_name, author_id, author_date, author_time)][commit_type][level] += displacement

# Base directory for output
base_dir = 'C:/Users/rujip/Desktop/SP2023-Greeedhub/CompetencyScore'  # Update this to your desired output path
csv_dir = os.path.join(base_dir, 'CSV')
json_dir = os.path.join(base_dir, 'JSON')

# Ensure base directories exist
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(json_dir, exist_ok=True)

# Process and write data for each commit
for key, scores in scores_dict.items():
    commit_hash, project_name, author_id, author_date, author_time = key
    after_scores = scores['after']
    before_scores = scores.get('before', {})
    difference_scores = {level: after_scores.get(level, 0) - before_scores.get(level, 0) for level in set(after_scores) | set(before_scores)}

    # File names
    filename_suffix = f"{commit_hash}_summary_{author_date}_{author_time}"
    csv_filename = os.path.join(csv_dir, project_name, author_id, f"{filename_suffix}.csv")
    json_filename = os.path.join(json_dir, project_name, author_id, f"{filename_suffix}.json")
    
    # Ensure directories for files exist
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    os.makedirs(os.path.dirname(json_filename), exist_ok=True)
    
    # CSV data
    csv_data = []
    for level in difference_scores:
        csv_data.append([commit_hash, project_name, author_id, author_date, author_time, level, after_scores.get(level, 0), before_scores.get(level, 0), difference_scores[level]])
    pd.DataFrame(csv_data, columns=["CommitHash", "ProjectName", "AuthorID", "AuthorDateFormat", "AuthorTimeFormat", "Level", "After", "Before", "Difference"]).to_csv(csv_filename, index=False)
    
    # JSON data
    json_data = {
        "CommitHash": commit_hash,
        "ProjectName": project_name,
        "AuthorID": author_id,
        "AuthorDateFormat": author_date,
        "AuthorTimeFormat": author_time,
        "Levels": {
            "After": after_scores,
            "Before": before_scores,
            "Difference": difference_scores
        }
    }
    with open(json_filename, 'w') as f_json:
        json.dump(json_data, f_json, indent=4)
