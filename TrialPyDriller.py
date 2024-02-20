# import os
# import csv
# from pydriller import Repository
# from urllib.parse import urlparse

# # URL of the repository
# repo_url = "https://github.com/ishepard/pydriller"

# # Extract project name from the repository URL
# parsed_url = urlparse(repo_url)
# project_name = parsed_url.path.split('/')[-1]

# # Directory paths for CSV and Python files
# csv_directory = 'PythonCommits_data'
# python_files_directory = 'PythonFiles'
# csv_file_name = f"{project_name}_data.csv"
# csv_file_path = os.path.join(csv_directory, csv_file_name)

# # Create directories if they don't exist
# os.makedirs(csv_directory, exist_ok=True)
# os.makedirs(python_files_directory, exist_ok=True)

# def format_filename(commit_hash, project_name, author_name, author_date, suffix, index=None):
#     date_formatted = author_date.strftime("%Y%m%d") if author_date else "unknown_date"
#     file_name = f"{commit_hash}_{project_name}_{author_name}_{date_formatted}"
#     if index is not None:
#         file_name += f"_{index}"
#     file_name += f"_{suffix}.py"
#     return file_name

# def write_code_to_file(project_name, author_name, commit_hash, author_date, code, suffix, index=None):
#     if code is None:
#         return None

#     file_name = format_filename(commit_hash, project_name, author_name, author_date, suffix, index)
#     hash_directory = os.path.join(python_files_directory, project_name, author_name, commit_hash)
#     os.makedirs(hash_directory, exist_ok=True)

#     file_path = os.path.join(hash_directory, file_name)
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(code)

#     return file_path

# def extract_data(repo_url, csv_file_path):
#     with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file)
#         writer.writerow(["CommitHash", "ProjectName", "AuthorName", "AuthorEmail", 
#                          "AuthorDate", "AuthorTimezone", "ModifiedFilename", "ChangeTypes", "AddedLines",
#                          "DeletedLines", "SourceCodeBeforeFilePath", "SourceCodeFilePath"])

#         hash_file_index = {}  # To track the index for each hash
#         for count, commit in enumerate(Repository(repo_url).traverse_commits(), start=1):
#             try:
#                 for modified_file in commit.modified_files:
#                     if modified_file.filename.endswith('.py'):
#                         index = hash_file_index.get(commit.hash, 1)
#                         before_file_path = write_code_to_file(commit.project_name, commit.author.name, commit.hash, commit.author_date, modified_file.source_code_before, "before", index)
#                         after_file_path = write_code_to_file(commit.project_name, commit.author.name, commit.hash, commit.author_date, modified_file.source_code, "after", index)
#                         writer.writerow([
#                             commit.hash,
#                             project_name,
#                             commit.author.name,
#                             commit.author.email,
#                             commit.author_date,
#                             commit.author_timezone,
#                             modified_file.filename,
#                             modified_file.change_type.name,
#                             modified_file.added_lines,
#                             modified_file.deleted_lines,
#                             before_file_path,
#                             after_file_path
#                         ])

#                         hash_file_index[commit.hash] = index + 1  # Increment index for this hash
#                         print(f'Files for commit hash {commit.hash} have been recorded.')

#                 if count % 10 == 0:
#                     print(f"\nCompleted {count} commits...\n")
#             except Exception as e:  # Catch all exceptions to avoid crashing
#                 print(f"Error encountered at commit {commit.hash}: {e}. Skipping this commit.")

# # Running the extraction function
# extract_data(repo_url, csv_file_path)

# print("Data extraction complete. CSV file saved at:", csv_file_path)
# import os
# import csv
# import hashlib
# from pydriller import Repository
# from urllib.parse import urlparse
# import shutil
# import stat

# # Enhanced error handling for directory deletion
# def onerror(func, path, exc_info):
#     """
#     Error handler for `shutil.rmtree`.
#     If the error is due to an access error (read only file),
#     it attempts to add write permission and then retries.
#     If the error is for another reason, it re-raises the error.
#     Usage: `shutil.rmtree(path, onerror=onerror)`
#     """
#     print(f"Error handling path: {path}")
#     if not os.access(path, os.W_OK):
#         os.chmod(path, stat.S_IWUSR)
#         func(path)
#     else:
#         raise

# def safe_delete_directory(path):
#     """Safely delete a directory and handle errors."""
#     if os.path.exists(path):
#         shutil.rmtree(path, onerror=onerror)

# def hash_author_email(email):
#     """Hashes author email for privacy."""
#     return hashlib.sha256(email.encode()).hexdigest()[:8]  # Shorten the hash for simplicity

# def format_filename(commit_hash, project_name, author_id, author_date, suffix, index=None):
#     """Formats filename for consistency."""
#     date_formatted = author_date.strftime("%Y%m%d")
#     file_name = f"{commit_hash}_{project_name}_{author_id}_{date_formatted}_{suffix}"
#     if index is not None:
#         file_name += f"_{index}"
#     file_name += ".py"
#     return file_name

# def write_code_to_file(directory, filename, code):
#     """Writes code to a file, creating directories as needed."""
#     if code is None:
#         return None

#     try:
#         os.makedirs(directory, exist_ok=True)
#         file_path = os.path.join(directory, filename)
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(code)
#         return file_path
#     except Exception as e:
#         print(f"Failed to write file {filename} at {directory}: {e}")
#         return None

# def extract_data(repo_url):
#     """Extracts data from repository commits and writes to CSV."""
#     csv_file_path = os.path.join(csv_directory, f"{project_name}_data.csv")
#     author_email_map_path = os.path.join(csv_directory, f"{project_name}_AuthorEmail.csv")

#     with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file, \
#          open(author_email_map_path, 'w', newline='', encoding='utf-8') as author_email_file:

#         csv_writer = csv.writer(csv_file)
#         author_email_writer = csv.writer(author_email_file)

#         csv_writer.writerow(["CommitHash", "ProjectName", "AuthorID", "AuthorDate", "AuthorTimezone", "ModifiedFilename", "ChangeType", "AddedLines", "DeletedLines", "SourceCodeBeforeFilePath", "SourceCodeFilePath"])
#         author_email_writer.writerow(["AuthorID", "AuthorEmail"])

#         author_ids = {}

#         for commit in Repository(repo_url).traverse_commits():
#             print(f"Processing commit {commit.hash}...")

#             for index, modified_file in enumerate(commit.modified_files, start=1):
#                 if modified_file.filename.endswith('.py'):
#                     print(f"  File #{index}: {modified_file.filename}")

#                     author_email = commit.author.email
#                     author_id = hash_author_email(author_email)
#                     if author_email not in author_ids:
#                         author_ids[author_email] = author_id
#                         author_email_writer.writerow([author_id, author_email])

#                     commit_directory = os.path.join(python_files_directory, author_id, commit.hash)
#                     before_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "before", index)
#                     after_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "after", index)

#                     before_file_path = write_code_to_file(commit_directory, before_filename, modified_file.source_code_before)
#                     after_file_path = write_code_to_file(commit_directory, after_filename, modified_file.source_code)

#                     csv_writer.writerow([
#                         commit.hash,
#                         project_name,
#                         author_id,
#                         commit.author_date.strftime("%Y-%m-%d %H:%M:%S"),
#                         commit.author_timezone,
#                         modified_file.filename,
#                         modified_file.change_type.name,
#                         modified_file.added_lines,
#                         modified_file.deleted_lines,
#                         before_file_path,
#                         after_file_path
#                     ])

# # Main execution starts here
# repo_url = "https://github.com/ishepard/pydriller"
# parsed_url = urlparse(repo_url)
# project_name = parsed_url.path.split('/')[-1]

# # Delete directories with the same project name as the inputted repository URL
# safe_delete_directory(os.path.join('PythonFiles', project_name))
# safe_delete_directory(os.path.join('PythonCommits_data', project_name))

# csv_directory = os.path.join('PythonCommits_data', project_name)
# python_files_directory = os.path.join('PythonFiles', project_name)

# # Clean up before starting
# safe_delete_directory(csv_directory)
# # No need to delete python_files_directory as it's empty initially

# # Re-create directories
# os.makedirs(csv_directory, exist_ok=True)

# print("Starting data extraction...")
# extract_data(repo_url)
# print("Data extraction completed.")

# import os
# import csv
# import hashlib
# from pydriller import Repository
# from urllib.parse import urlparse
# import shutil
# import stat
# from datetime import datetime, timedelta
# import pytz

# # Enhanced error handling for directory deletion
# def onerror(func, path, exc_info):
#     """
#     Error handler for `shutil.rmtree`.
#     If the error is due to an access error (read only file),
#     it attempts to add write permission and then retries.
#     If the error is for another reason, it re-raises the error.
#     Usage: `shutil.rmtree(path, onerror=onerror)`
#     """
#     print(f"Error handling path: {path}")
#     if not os.access(path, os.W_OK):
#         os.chmod(path, stat.S_IWUSR)
#         func(path)
#     else:
#         raise

# def safe_delete_directory(path):
#     """Safely delete a directory and handle errors."""
#     if os.path.exists(path):
#         shutil.rmtree(path, onerror=onerror)

# def hash_author_email(email):
#     """Hashes author email for privacy."""
#     return hashlib.sha256(email.encode()).hexdigest()[:8]  # Shorten the hash for simplicity

# def format_filename(commit_hash, project_name, author_id, author_date, suffix, index=None):
#     """Formats filename for consistency."""
#     date_formatted = author_date.strftime("%Y%m%d_%H%M%S")
#     file_name = f"{commit_hash}_{project_name}_{author_id}_{date_formatted}_{suffix}"
#     if index is not None:
#         file_name += f"_{index}"
#     file_name += ".py"
#     return file_name

# def write_code_to_file(directory, filename, code):
#     """Writes code to a file, creating directories as needed."""
#     if code is None:
#         return None

#     try:
#         os.makedirs(directory, exist_ok=True)
#         file_path = os.path.join(directory, filename)
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(code)
#         return file_path
#     except Exception as e:
#         print(f"Failed to write file {filename} at {directory}: {e}")
#         return None

# def extract_data(repo_url):
#     """Extracts data from repository commits and writes to CSV."""
#     csv_file_path = os.path.join(csv_directory, f"{project_name}_data.csv")
#     author_email_map_path = os.path.join(csv_directory, f"{project_name}_AuthorEmail.csv")

#     with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file, \
#          open(author_email_map_path, 'w', newline='', encoding='utf-8') as author_email_file:

#         csv_writer = csv.writer(csv_file)
#         author_email_writer = csv.writer(author_email_file)

#         csv_writer.writerow(["CommitHash", "ProjectName", "AuthorID", "AuthorDate", "AuthorTimezone", "ModifiedFilename", "ChangeType", "AddedLines", "DeletedLines", "SourceCodeBeforeFilePath", "SourceCodeFilePath"])
#         author_email_writer.writerow(["AuthorID", "AuthorEmail"])

#         author_ids = {}

#         for commit in Repository(repo_url).traverse_commits():
#             print(f"Processing commit {commit.hash}...")

#             for index, modified_file in enumerate(commit.modified_files, start=1):
#                 if modified_file.filename.endswith('.py'):
#                     print(f"  File #{index}: {modified_file.filename}")

#                     author_email = commit.author.email
#                     author_id = hash_author_email(author_email)
#                     if author_email not in author_ids:
#                         author_ids[author_email] = author_id
#                         author_email_writer.writerow([author_id, author_email])

#                     commit_directory = os.path.join(python_files_directory, author_id, commit.hash)
#                     before_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "before", index)
#                     after_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "after", index)

#                     # Normalize timezone
#                     normalized_date = commit.author_date.astimezone(pytz.timezone('UTC'))
#                     normalized_timezone = '+0000' if normalized_date.utcoffset() == timedelta(0) else normalized_date.strftime('%z')

#                     before_file_path = write_code_to_file(commit_directory, before_filename, modified_file.source_code_before)
#                     after_file_path = write_code_to_file(commit_directory, after_filename, modified_file.source_code)

#                     csv_writer.writerow([
#                         commit.hash,
#                         project_name,
#                         author_id,
#                         normalized_date.strftime("%Y-%m-%d %H:%M:%S"),
#                         normalized_timezone,
#                         modified_file.filename,
#                         modified_file.change_type.name,
#                         modified_file.added_lines,
#                         modified_file.deleted_lines,
#                         before_file_path,
#                         after_file_path
#                     ])

# # Main execution starts here
# repo_url = "https://github.com/ishepard/pydriller"
# parsed_url = urlparse(repo_url)
# project_name = parsed_url.path.split('/')[-1]

# # Delete directories with the same project name as the inputted repository URL
# safe_delete_directory(os.path.join('PythonFiles', project_name))
# safe_delete_directory(os.path.join('PythonCommits_data', project_name))

# csv_directory = os.path.join('PythonCommits_data', project_name)
# python_files_directory = os.path.join('PythonFiles', project_name)

# # Clean up before starting
# safe_delete_directory(csv_directory)
# # No need to delete python_files_directory as it's empty initially

# # Re-create directories
# os.makedirs(csv_directory, exist_ok=True)

# print("Starting data extraction...")
# extract_data(repo_url)
# print("Data extraction completed.")

# import os
# import csv
# import hashlib
# from pydriller import Repository
# from urllib.parse import urlparse
# import shutil
# import stat
# from datetime import datetime, timedelta
# import pytz

# # Enhanced error handling for directory deletion
# def onerror(func, path, exc_info):
#     """
#     Error handler for `shutil.rmtree`.
#     If the error is due to an access error (read only file),
#     it attempts to add write permission and then retries.
#     If the error is for another reason, it re-raises the error.
#     Usage: `shutil.rmtree(path, onerror=onerror)`
#     """
#     print(f"Error handling path: {path}")
#     if not os.access(path, os.W_OK):
#         os.chmod(path, stat.S_IWUSR)
#         func(path)
#     else:
#         raise

# def safe_delete_directory(path):
#     """Safely delete a directory and handle errors."""
#     if os.path.exists(path):
#         shutil.rmtree(path, onerror=onerror)

# def hash_author_email(email):
#     """Hashes author email for privacy."""
#     return hashlib.sha256(email.encode()).hexdigest()[:8]  # Shorten the hash for simplicity

# def format_filename(commit_hash, project_name, author_id, author_date, suffix, index=None):
#     """Formats filename for consistency."""
#     date_formatted = author_date.strftime("%Y%m%d_%H%M%S")
#     file_name = f"{commit_hash}_{project_name}_{author_id}_{date_formatted}_{suffix}"
#     if index is not None:
#         file_name += f"_{index}"
#     file_name += ".py"
#     return file_name

# def write_code_to_file(directory, filename, code):
#     """Writes code to a file, creating directories as needed."""
#     if code is None:
#         return None

#     try:
#         os.makedirs(directory, exist_ok=True)
#         file_path = os.path.join(directory, filename)
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(code)
#         return file_path
#     except Exception as e:
#         print(f"Failed to write file {filename} at {directory}: {e}")
#         return None

# def extract_data(repo_url):
#     """Extracts data from repository commits and writes to CSV."""
#     csv_file_path = os.path.join(csv_directory, f"{project_name}_data.csv")
#     author_email_map_path = os.path.join(csv_directory, f"{project_name}_AuthorEmail.csv")

#     with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file, \
#          open(author_email_map_path, 'w', newline='', encoding='utf-8') as author_email_file:

#         csv_writer = csv.writer(csv_file)
#         author_email_writer = csv.writer(author_email_file)

#         csv_writer.writerow(["CommitHash", "ProjectName", "AuthorID", "AuthorDate", "AuthorTimezone", "ModifiedFilename", "ChangeType", "AddedLines", "DeletedLines", "SourceCodeBeforeFilePath", "SourceCodeFilePath"])
#         author_email_writer.writerow(["AuthorID", "AuthorEmail"])

#         author_ids = {}

#         for commit in Repository(repo_url).traverse_commits():
#             print(f"Processing commit {commit.hash}...")

#             for index, modified_file in enumerate(commit.modified_files, start=1):
#                 if modified_file.filename.endswith('.py'):
#                     print(f"  File #{index}: {modified_file.filename}")

#                     author_email = commit.author.email
#                     author_id = hash_author_email(author_email)
#                     if author_email not in author_ids:
#                         author_ids[author_email] = author_id
#                         author_email_writer.writerow([author_id, author_email])

#                     commit_directory = os.path.join(python_files_directory, author_id, commit.hash)
#                     before_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "before", index)
#                     after_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "after", index)

#                     # Normalize timezone
#                     normalized_date = commit.author_date.astimezone(pytz.timezone('UTC'))
#                     normalized_timezone = '+0000' if normalized_date.utcoffset() == timedelta(0) else normalized_date.strftime('%z')

#                     before_file_path = write_code_to_file(commit_directory, before_filename, modified_file.source_code_before)
#                     after_file_path = write_code_to_file(commit_directory, after_filename, modified_file.source_code)

#                     csv_writer.writerow([
#                         commit.hash,
#                         project_name,
#                         author_id,
#                         normalized_date.strftime("%Y-%m-%d %H:%M:%S"),
#                         normalized_timezone,
#                         modified_file.filename,
#                         modified_file.change_type.name,
#                         modified_file.added_lines,
#                         modified_file.deleted_lines,
#                         before_file_path,
#                         after_file_path
#                     ])

# # Main execution starts here
# repo_urls = [
#     "https://github.com/ishepard/pydriller",
#     "https://github.com/keras-team/keras.git"
# ]

# for repo_url in repo_urls:
#     parsed_url = urlparse(repo_url)
#     project_name = parsed_url.path.split('/')[-1]

#     # Delete directories with the same project name as the inputted repository URL
#     safe_delete_directory(os.path.join('PythonFiles', project_name))
#     safe_delete_directory(os.path.join('PythonCommits_data', project_name))

#     csv_directory = os.path.join('PythonCommits_data', project_name)
#     python_files_directory = os.path.join('PythonFiles', project_name)

#     # Clean up before starting
#     safe_delete_directory(csv_directory)
#     # No need to delete python_files_directory as it's empty initially

#     # Re-create directories
#     os.makedirs(csv_directory, exist_ok=True)

#     print("Starting data extraction...")
#     extract_data(repo_url)
#     print("Data extraction completed.")

# import os
# import csv
# import hashlib
# from pydriller import Repository
# from urllib.parse import urlparse
# import shutil
# import stat
# from datetime import datetime, timedelta
# import pytz

# # Enhanced error handling for directory deletion
# def onerror(func, path, exc_info):
#     """
#     Error handler for `shutil.rmtree`.
#     If the error is due to an access error (read only file),
#     it attempts to add write permission and then retries.
#     If the error is for another reason, it re-raises the error.
#     Usage: `shutil.rmtree(path, onerror=onerror)`
#     """
#     print(f"Error handling path: {path}")
#     if not os.access(path, os.W_OK):
#         os.chmod(path, stat.S_IWUSR)
#         func(path)
#     else:
#         raise

# def safe_delete_directory(path):
#     """Safely delete a directory and handle errors."""
#     if os.path.exists(path):
#         shutil.rmtree(path, onerror=onerror)

# def hash_author_email(email):
#     """Hashes author email for privacy."""
#     return hashlib.sha256(email.encode()).hexdigest()[:8]  # Shorten the hash for simplicity

# def format_filename(commit_hash, project_name, author_id, author_date, suffix, index=None):
#     """Formats filename for consistency."""
#     date_formatted = author_date.strftime("%Y%m%d_%H%M%S")
#     file_name = f"{commit_hash}_{project_name}_{author_id}_{date_formatted}_{suffix}"
#     if index is not None:
#         file_name += f"_{index}"
#     file_name += ".py"
#     return file_name

# def write_code_to_file(directory, filename, code):
#     """Writes code to a file, creating directories as needed."""
#     if code is None:
#         return None

#     try:
#         os.makedirs(directory, exist_ok=True)
#         file_path = os.path.join(directory, filename)
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(code)
#         return file_path
#     except Exception as e:
#         print(f"Failed to write file {filename} at {directory}: {e}")
#         return None

# def extract_data(repo_url):
#     """Extracts data from repository commits and writes to CSV."""
#     parsed_url = urlparse(repo_url)
#     project_name = parsed_url.path.split('/')[-1]

#     csv_directory = 'PythonCommits_data'
#     python_files_directory = os.path.join('PythonFiles', project_name)
#     author_email_directory = 'PythonAuthorEmail_data'

#     # Create directories if they don't exist
#     os.makedirs(csv_directory, exist_ok=True)
#     os.makedirs(author_email_directory, exist_ok=True)

#     # Delete directories with the same project name as the inputted repository URL
#     safe_delete_directory(python_files_directory)

#     csv_file_path = os.path.join(csv_directory, f"{project_name}_data.csv")
#     author_email_map_path = os.path.join(author_email_directory, f"{project_name}_AuthorEmail.csv")

#     with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file, \
#          open(author_email_map_path, 'w', newline='', encoding='utf-8') as author_email_file:

#         csv_writer = csv.writer(csv_file)
#         author_email_writer = csv.writer(author_email_file)

#         csv_writer.writerow(["CommitHash", "ProjectName", "AuthorID", "AuthorDate", "AuthorTimezone", "ModifiedFilename", "ChangeType", "AddedLines", "DeletedLines", "SourceCodeBeforeFilePath", "SourceCodeFilePath"])
#         author_email_writer.writerow(["AuthorID", "AuthorEmail"])

#         author_ids = {}

#         for commit in Repository(repo_url).traverse_commits():
#             print(f"Processing commit {commit.hash}...")

#             for index, modified_file in enumerate(commit.modified_files, start=1):
#                 if modified_file.filename.endswith('.py'):
#                     print(f"  File #{index}: {modified_file.filename}")

#                     author_email = commit.author.email
#                     author_id = hash_author_email(author_email)
#                     if author_email not in author_ids:
#                         author_ids[author_email] = author_id
#                         author_email_writer.writerow([author_id, author_email])

#                     commit_directory = os.path.join(python_files_directory, author_id, commit.hash)
#                     before_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "before", index)
#                     after_filename = format_filename(commit.hash, project_name, author_id, commit.author_date, "after", index)

#                     # Normalize timezone
#                     normalized_date = commit.author_date.astimezone(pytz.timezone('UTC'))
#                     normalized_timezone = '+0000' if normalized_date.utcoffset() == timedelta(0) else normalized_date.strftime('%z')

#                     before_file_path = write_code_to_file(commit_directory, before_filename, modified_file.source_code_before)
#                     after_file_path = write_code_to_file(commit_directory, after_filename, modified_file.source_code)

#                     csv_writer.writerow([
#                         commit.hash,
#                         project_name,
#                         author_id,
#                         normalized_date.strftime("%Y-%m-%d %H:%M:%S"),
#                         normalized_timezone,
#                         modified_file.filename,
#                         modified_file.change_type.name,
#                         modified_file.added_lines,
#                         modified_file.deleted_lines,
#                         before_file_path,
#                         after_file_path
#                     ])

# # Main execution starts here
# repo_urls = [
#     "https://github.com/ishepard/pydriller"
# ]

# for repo_url in repo_urls:
#     print(f"Processing repository: {repo_url}")
#     extract_data(repo_url)
#     print("Data extraction completed.")

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
        with open(file_path, 'wb') as file:  # Open in binary mode
            file.write(code.encode('utf-8'))  # Manually encode the data before writing
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
