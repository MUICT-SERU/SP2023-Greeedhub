# Code for TrialPyDriller.py
import os
import csv
import hashlib
from pydriller import Repository
from urllib.parse import urlparse
import shutil
import stat
from datetime import datetime, timedelta
import pytz

# Enhanced error handling for directory deletion
def onerror(func, path, exc_info):
    """
    Error handler for `shutil.rmtree`.
    If the error is due to an access error (read only file),
    it attempts to add write permission and then retries.
    If the error is for another reason, it re-raises the error.
    Usage: `shutil.rmtree(path, onerror=onerror)`
    """
    print(f"Error handling path: {path}")
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def safe_delete_directory(path):
    """Safely delete a directory and handle errors."""
    if os.path.exists(path):
        shutil.rmtree(path, onerror=onerror)

def hash_author_email(email):
    """Hashes author email for privacy."""
    return hashlib.sha256(email.encode()).hexdigest()[:8]  # Shorten the hash for simplicity

def format_filename(commit_hash, project_name, author_id, author_date, suffix, index=None):
    """Formats filename for consistency."""
    date_formatted = author_date.strftime("%Y%m%d_%H%M%S")
    file_name = f"{commit_hash}_{project_name}_{author_id}_{date_formatted}_{suffix}"
    if index is not None:
        file_name += f"_{index}"
    file_name += ".py"
    return file_name

def write_code_to_file(directory, filename, code):
    """Writes code to a file, creating directories as needed."""
    if code is None:
        return None

    try:
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w', newline='', encoding='utf-8') as file:  # Specify encoding as 'utf-8'
            file.write(code)
        return file_path
    except Exception as e:
        print(f"Failed to write file {filename} at {directory}: {e}")
        return None

def extract_data(repo_url):
    """Extracts data from repository commits and writes to CSV."""
    parsed_url = urlparse(repo_url)
    project_name = parsed_url.path.split('/')[-1]

    csv_directory = 'PythonCommits_data'
    python_files_directory = os.path.join('PythonFiles', project_name)
    author_email_directory = 'PythonAuthorEmail_data'

    # Create directories if they don't exist
    os.makedirs(csv_directory, exist_ok=True)
    os.makedirs(author_email_directory, exist_ok=True)

    # Delete directories with the same project name as the inputted repository URL
    safe_delete_directory(python_files_directory)

    csv_file_path = os.path.join(csv_directory, f"{project_name}_data.csv")
    author_email_map_path = os.path.join(author_email_directory, f"{project_name}_AuthorEmail.csv")

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file, \
         open(author_email_map_path, 'w', newline='', encoding='utf-8') as author_email_file:

        csv_writer = csv.writer(csv_file)
        author_email_writer = csv.writer(author_email_file)

        csv_writer.writerow(["CommitHash", "ProjectName", "AuthorID", "AuthorDate", "AuthorTimezone", "ModifiedFilename", "ChangeType", "AddedLines", "DeletedLines", "SourceCodeBeforeFilePath", "SourceCodeFilePath"])
        author_email_writer.writerow(["AuthorID", "AuthorEmail"])

        author_ids = {}

        for commit in Repository(repo_url).traverse_commits():
            print(f"Processing commit {commit.hash}...")

            for index, modified_file in enumerate(commit.modified_files, start=1):
                if modified_file.filename.endswith('.py'):
                    print(f"  File #{index}: {modified_file.filename}")

                    author_email = commit.author.email
                    author_id = hash_author_email(author_email)
                    if author_email not in author_ids:
                        author_ids[author_email] = author_id
                        author_email_writer.writerow([author_id, author_email])

                    commit_directory = os.path.join(python_files_directory, author_id, commit.hash)
                    before_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "before", index)
                    after_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "after", index)

                    # Normalize timezone
                    normalized_date = commit.author_date.astimezone(pytz.timezone('UTC'))
                    normalized_timezone = '+0000' if normalized_date.utcoffset() == timedelta(0) else normalized_date.strftime('%z')

                    before_file_path = write_code_to_file(commit_directory, before_filename, modified_file.source_code_before)
                    after_file_path = write_code_to_file(commit_directory, after_filename, modified_file.source_code)

                    csv_writer.writerow([
                        commit.hash,
                        project_name,
                        author_id,
                        normalized_date.strftime("%Y-%m-%d %H:%M:%S"),
                        normalized_timezone,
                        modified_file.filename,
                        modified_file.change_type.name,
                        modified_file.added_lines,
                        modified_file.deleted_lines,
                        before_file_path,
                        after_file_path
                    ])

# Main execution starts here
repo_urls = [
    "https://github.com/ishepard/pydriller"
]

for repo_url in repo_urls:
    print(f"Processing repository: {repo_url}")
    extract_data(repo_url)
    print("Data extraction completed.")
