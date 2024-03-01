import pandas as pd
import git

def get_last_commit_date(repo_path):
    repo = git.Repo(repo_path)
    last_commit = repo.head.commit
    return last_commit.committed_datetime

# Read the dataset containing project information
data = pd.read_csv('DataPyPI.csv')

# Add a column for LastCommitDate
data['LastCommitDate'] = ""

# Iterate over each project
for index, row in data.iterrows():
    project_name = row['ProjectName']
    github_url = row['URL']  # Assuming GitHub URL is available in the dataset

    if github_url:
        try:
            # Get the path to the local clone of the GitHub repository
            repo_path = f'/path/to/your/local/repo/{project_name}'

            # Get the last commit date
            last_commit_date = get_last_commit_date(repo_path)

            # Record the last commit date in the dataset
            data.at[index, 'LastCommitDate'] = last_commit_date
            print(f"Last commit date for project {project_name}: {last_commit_date}")
        except Exception as e:
            print(f"Error processing project {project_name}: {e}")

# Save the updated dataset
data.to_csv('DataPyPI_LastCommitDate.csv', index=False)
print("Updated dataset saved to DataPyPI_LastCommitDate.csv")
