from pydriller import Repository
import csv
import os

# Replace the URL with the actual GitHub repository URL
repo_url = 'https://github.com/apache/airflow.git'
output_folder = 'path/to/output_folder'

def replace_none_values(data):
    # Replace None values in data dictionary with N/A (NULL Value)
    for key, value in data.items():
        if value is None:
            data[key] = "N/A"  # You can use any other placeholder if you prefer
    return data

def save_commit_data_to_csv(commit_data):
    output_filename = os.path.join(output_folder, 'all_python_commits.csv')
    mode = 'a'  # Append mode
    if not os.path.exists(output_filename):
        # If the file doesn't exist, create and write the header
        mode = 'w'
    with open(output_filename, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'hash', 'author_name', 'author_email', 'committer_name', 'committer_email',
            'author_date', 'author_timezone', 'committer_date', 'committer_timezone',
            'branches', 'in_main_branch', 'merge', 'modified_files',
            'project_name', 'project_path', 'old_path', 'new_path', 'filename', 'diff', 'diff_parsed',
            'added_lines', 'deleted_lines', 'source_code', 'source_code_before',
            'methods', 'methods_before', 'changed_methods'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if mode == 'w':
            writer.writeheader()

        for data in commit_data:
            data = replace_none_values(data)
            writer.writerow(data)

def extract_commit_data(commit):
    commit_data = []
    if commit.modified_files:
        for modification in commit.modified_files:
            try:
                if modification.filename.endswith('.py'):
                    print(f"==> Extract commit data in file path: '{modification.filename}' with Commit SHA: '{commit.hash}'")
                    data = {
                        'hash': commit.hash,
                        'author_name': commit.author.name,
                        'author_email': commit.author.email,
                        'committer_name': commit.committer.name,
                        'committer_email': commit.committer.email,
                        'author_date': commit.author_date,
                        'author_timezone': commit.author_timezone,
                        'committer_date': commit.committer_date,
                        'committer_timezone': commit.committer_timezone,
                        'branches': ", ".join(commit.branches),
                        'in_main_branch': commit.in_main_branch,
                        'merge': commit.merge,
                        'modified_files': modification.new_path,
                        'project_name': commit.project_name,
                        'project_path': commit.project_path,
                        'old_path': modification.old_path,
                        'new_path': modification.new_path,
                        'filename': modification.filename,
                        'diff': modification.diff,
                        'diff_parsed': modification.diff_parsed,
                        'added_lines': modification.added_lines,
                        'deleted_lines': modification.deleted_lines,
                        'source_code': modification.source_code,
                        'source_code_before': modification.source_code_before,
                        'methods': modification.methods,
                        'methods_before': modification.methods_before,
                        'changed_methods': modification.changed_methods,
                    }
                    commit_data.append(data)
                    print(f"data: '{data}'")
                    save_commit_data_to_csv([data])  # Save the commit data immediately after extraction
            except Exception as e:
                print(f"Error processing commit '{commit.hash}': {str(e)}")
                continue
    return commit_data

def main():
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    for commit in Repository(repo_url).traverse_commits():
        extract_commit_data(commit)

    print(f"All Python commits in Apache Airflow are recorded in 'all_python_commits.csv'")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
