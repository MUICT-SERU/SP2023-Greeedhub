# import subprocess
# import os
# import json
# import csv
# from collections import defaultdict
# from pathlib import Path

# # Define the directories
# pycefr_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\pycefr'  # Path to the PyCEFR scripts
# json_data_dir = os.path.join(pycefr_dir, 'DATA_JSON')  # Where JSON data will be stored
# output_csv_dir = 'CompetencyScore_CSV'  # Output directory for CSV files
# output_json_dir = 'CompetencyScore_JSON'  # Output directory for JSON files

# # Ensure output directories exist
# Path(output_csv_dir).mkdir(parents=True, exist_ok=True)
# Path(output_json_dir).mkdir(parents=True, exist_ok=True)

# def run_pycefr_analysis():
#     """
#     Runs the PyCEFR analysis by executing its scripts and generating JSON data.
#     """
#     # Navigate to the PyCEFR directory
#     os.chdir(pycefr_dir)
    
#     # Run PyCEFR scripts
#     subprocess.run(['python3', 'dict.py'], check=True)
#     subprocess.run(['python3', 'pycerfl.py', 'directory', '../PythonFiles'], check=True)
    
#     # Navigate back to the original script directory if needed
#     # os.chdir('path/to/original/directory')

# def process_json_files():
#     """
#     Processes JSON files generated by PyCEFR to extract competency levels and 
#     generate summary CSV and JSON files.
#     """
#     for json_file in Path(json_data_dir).glob('*.json'):
#         with open(json_file) as f:
#             data = json.load(f)
        
#         # Initialize dictionaries for aggregated competency levels
#         after_sum, before_sum, diff = defaultdict(int), defaultdict(int), defaultdict(int)
        
#         # Assume 'data' is structured as specified; adjust processing as needed
#         for commit_hash, files in data.items():
#             process_commit_data(commit_hash, files, after_sum, before_sum)
        
#         # Calculate differences
#         for level in after_sum:
#             diff[level] = after_sum[level] - before_sum[level]
        
#         # Generate summary files
#         generate_summary_files(commit_hash, after_sum, before_sum, diff)

# def process_commit_data(commit_hash, files, after_sum, before_sum):
#     """
#     Processes individual commit data to aggregate competency levels.
#     Adjust this function based on the actual structure of your JSON data.
#     """
#     for file, content in files.items():
#         if 'after' in file:
#             for level, score in content['Levels'].items():
#                 after_sum[level] += score
#         elif 'before' in file:
#             for level, score in content['Levels'].items():
#                 before_sum[level] += score

# def generate_summary_files(commit_hash, after_sum, before_sum, diff):
#     """
#     Generates CSV and JSON summary files for competency levels.
#     """
#     # Define paths for CSV and JSON files
#     csv_path = os.path.join(output_csv_dir, f'{commit_hash}_summary.csv')
#     json_path = os.path.join(output_json_dir, f'{commit_hash}_summary.json')

#     # CSV output
#     with open(csv_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['Level', 'After', 'Before', 'Difference'])
#         for level in after_sum:
#             writer.writerow([level, after_sum[level], before_sum.get(level, 0), diff[level]])

#     # JSON output
#     with open(json_path, 'w') as jsonfile:
#         json.dump({'after': after_sum, 'before': before_sum, 'difference': diff}, jsonfile, indent=4)

# def main():
#     # Step 1: Run PyCEFR analysis
#     run_pycefr_analysis()
    
#     # Step 2: Process the JSON files to generate summaries
#     process_json_files()

#     print("Analysis and summary generation completed.")

# if __name__ == "__main__":
#     main()

# import subprocess
# import os
# import json
# import csv
# from collections import defaultdict
# from pathlib import Path

# # Define the directories
# pycefr_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\pycefr'  # Path to the PyCEFR scripts
# json_data_dir = os.path.join(pycefr_dir, 'DATA_JSON')  # Where JSON data will be stored
# output_dir = 'CompetencyScore'  # Output directory for CSV and JSON files

# # Ensure output directory exists
# Path(output_dir).mkdir(parents=True, exist_ok=True)

# def clone_pycefr_repository():
#     """
#     Clones the PyCEFR repository from GitHub.
#     """
#     try:
#         subprocess.run(['git', 'clone', 'https://github.com/anapgh/pycefr.git'], check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Error cloning PyCEFR repository: {e}")

# def run_pycefr_analysis():
#     """
#     Runs the PyCEFR analysis by executing its scripts and generating JSON data.
#     """
#     # Navigate to the PyCEFR directory
#     os.chdir(pycefr_dir)
    
#     # Run PyCEFR scripts
#     try:
#         subprocess.run(['python3', 'dict.py'], check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Error running 'dict.py': {e}")
    
#     try:
#         subprocess.run(['python3', 'pycerfl.py', 'directory', '../PythonFiles_PyCEFR'], check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Error running 'pycerfl.py': {e}")
    
#     # Navigate back to the original script directory if needed

# def process_json_files():
#     """
#     Processes JSON files generated by PyCEFR to extract competency levels and 
#     generate summary CSV and JSON files.
#     """
#     for json_file in Path(json_data_dir).glob('*.json'):
#         with open(json_file) as f:
#             data = json.load(f)
        
#         # Validate filename structure
#         file_parts = json_file.stem.split('_')
#         if len(file_parts) < 5:  # Ensuring there are at least 5 parts including incrementalNumber
#             print(f"Skipping file with unexpected name structure: {json_file.name}")
#             continue
        
#         commit_hash = file_parts[0]
#         project_name = '_'.join(file_parts[1:-3])  # Adjusted to join all parts that might be the project name
#         author_id = file_parts[-3]
#         author_date_format = file_parts[-2]

#         # Initialize dictionaries for aggregated competency levels
#         after_sum, before_sum, diff = defaultdict(int), defaultdict(int), defaultdict(int)
        
#         # Assume 'data' is structured as specified; adjust processing as needed
#         for _, files in data.items():
#             process_commit_data(files, after_sum, before_sum)
        
#         # Calculate differences
#         for level in after_sum:
#             diff[level] = after_sum[level] - before_sum[level]
        
#         # Generate summary files
#         generate_summary_files(commit_hash, project_name, author_id, author_date_format, after_sum, before_sum, diff)

# def process_commit_data(files, after_sum, before_sum):
#     """
#     Processes individual commit data to aggregate competency levels.
#     Adjust this function based on the actual structure of your JSON data.
#     """
#     for _, content in files.items():
#         for level, score in content['Levels'].items():
#             if 'after' in content['FileName']:
#                 after_sum[level] += score
#             elif 'before' in content['FileName']:
#                 before_sum[level] += score

# def generate_summary_files(commit_hash, project_name, author_id, author_date_format, after_sum, before_sum, diff):
#     """
#     Generates CSV and JSON summary files for competency levels.
#     """
#     # Define paths for CSV and JSON files
#     author_dir = os.path.join(output_dir, project_name, author_id)
#     Path(author_dir).mkdir(parents=True, exist_ok=True)
    
#     csv_path = os.path.join(author_dir, f'summary_{author_date_format}.csv')
#     json_path = os.path.join(author_dir, f'summary_{author_date_format}.json')

#     # CSV output
#     with open(csv_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['CommitHash', 'ProjectName', 'AuthorID', 'AuthorDateFormat', 'Level', 'After', 'Before', 'Difference'])
#         for level in after_sum:
#             writer.writerow([commit_hash, project_name, author_id, author_date_format, level, after_sum[level], before_sum.get(level, 0), diff[level]])

#     # JSON output
#     with open(json_path, 'w') as jsonfile:
#         json.dump({'CommitHash': commit_hash, 'ProjectName': project_name, 'AuthorID': author_id, 'AuthorDateFormat': author_date_format,
#                    'after': after_sum, 'before': before_sum, 'difference': diff}, jsonfile, indent=4)

# def main():
#     # Step 1: Clone PyCEFR repository
#     clone_pycefr_repository()

#     # Step 2: Run PyCEFR analysis
#     run_pycefr_analysis()
    
#     # Step 3: Process the JSON files to generate summaries
#     process_json_files()

#     print("Analysis and summary generation completed.")

# if __name__ == "__main__":
#     main()

# import subprocess
# import os
# import json
# import csv
# from collections import defaultdict
# from pathlib import Path

# # Define the directories
# pycefr_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\pycefr'  # Path to the PyCEFR scripts
# json_data_dir = os.path.join(pycefr_dir, 'DATA_JSON')  # Where JSON data will be stored
# output_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\CompetencyScore'  # Output directory for CSV and JSON files

# # Ensure output directory exists
# Path(output_dir).mkdir(parents=True, exist_ok=True)

# def clone_pycefr_repository():
#     """
#     Clones the PyCEFR repository from GitHub.
#     """
#     if not Path(pycefr_dir).exists():
#         try:
#             subprocess.run(['git', 'clone', 'https://github.com/anapgh/pycefr.git', pycefr_dir], check=True)
#             print("PyCEFR repository cloned successfully.")
#         except subprocess.CalledProcessError as e:
#             print(f"Error cloning PyCEFR repository: {e}")
#     else:
#         print("PyCEFR repository already exists.")

# def run_pycefr_analysis():
#     """
#     Runs the PyCEFR analysis by executing its scripts and generating JSON data.
#     """
#     # Navigate to the PyCEFR directory
#     os.chdir(pycefr_dir)
    
#     # Run PyCEFR scripts
#     try:
#         subprocess.run(['python', 'dict.py'], check=True)  # Adjust python command as needed
#     except subprocess.CalledProcessError as e:
#         print(f"Error running 'dict.py': {e}")
    
#     try:
#         subprocess.run(['python', 'pycerfl.py', 'directory', 'PythonFiles_PyCEFR'], check=True)  # Adjust the path as needed
#     except subprocess.CalledProcessError as e:
#         print(f"Error running 'pycerfl.py': {e}")
    
#     # Navigate back to the script's original directory if necessary
#     os.chdir(Path(__file__).parent)

# def process_json_files():
#     """
#     Processes JSON files generated by PyCEFR to extract competency levels and 
#     generate summary CSV and JSON files.
#     """
#     for json_file in Path(json_data_dir).glob('*.json'):
#         with open(json_file) as f:
#             data = json.load(f)
        
#         # Process each commit in the JSON file
#         for commit_hash, commit_data in data.items():
#             # Extract project name, author ID, and date from the first file name
#             first_file_name = next(iter(commit_data))
#             parts = first_file_name.split('_')
#             project_name, author_id, author_date_format = parts[1], parts[2], parts[3]
            
#             after_sum, before_sum = defaultdict(int), defaultdict(int)
            
#             # Process each file in the commit
#             for file_name, file_data in commit_data.items():
#                 status = file_name.split('_')[4]  # 'after' or 'before'
#                 for level, score in file_data['Levels'].items():
#                     if status == 'after':
#                         after_sum[level] += score
#                     else:  # status == 'before'
#                         before_sum[level] += score
            
#             # Calculate differences
#             diff = {level: after_sum[level] - before_sum.get(level, 0) for level in after_sum}
            
#             # Generate summary files
#             generate_summary_files(commit_hash, project_name, author_id, author_date_format, after_sum, before_sum, diff)

# def generate_summary_files(commit_hash, project_name, author_id, author_date_format, after_sum, before_sum, diff):
#     """
#     Generates CSV and JSON summary files for a single commit.
#     """
#     csv_dir = os.path.join(output_dir, 'CSV', project_name, author_id)
#     json_dir = os.path.join(output_dir, 'JSON', project_name, author_id)
#     Path(csv_dir).mkdir(parents=True, exist_ok=True)
#     Path(json_dir).mkdir(parents=True, exist_ok=True)
    
#     summary_base = f"{commit_hash}_summary_{author_date_format}"
#     csv_path = os.path.join(csv_dir, f"{summary_base}.csv")
#     json_path = os.path.join(json_dir, f"{summary_base}.json")
    
#     # Write CSV
#     with open(csv_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['CommitHash', 'ProjectName', 'AuthorID', 'AuthorDateFormat', 'Level', 'After', 'Before', 'Difference'])
#         for level in after_sum:
#             writer.writerow([commit_hash, project_name, author_id, author_date_format, level, after_sum[level], before_sum.get(level, 0), diff.get(level, 0)])
    
#     # Write JSON
#     summary_data = {
#         'CommitHash': commit_hash,
#         'ProjectName': project_name,
#         'AuthorID': author_id,
#         'AuthorDateFormat': author_date_format,
#         'Levels': {
#             'After': after_sum,
#             'Before': before_sum,
#             'Difference': diff
#         }
#     }
#     with open(json_path, 'w') as jsonfile:
#         json.dump(summary_data, jsonfile, indent=4)

# def main():
#     # Step 1: Clone PyCEFR repository
#     clone_pycefr_repository()

#     # Step 2: Run PyCEFR analysis
#     run_pycefr_analysis()
    
#     # Step 3: Process the JSON files to generate summaries
#     process_json_files()

#     print("Analysis and summary generation completed.")

# if __name__ == "__main__":
#     main()

# import subprocess
# import os
# import json
# import csv
# from collections import defaultdict
# from pathlib import Path

# # Define the directories
# pycefr_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\pycefr'  # Path to the PyCEFR scripts
# json_data_dir = os.path.join(pycefr_dir, 'DATA_JSON')  # Where JSON data will be stored
# output_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\CompetencyScore'  # Output directory for CSV and JSON files

# # Ensure output directory exists
# Path(output_dir).mkdir(parents=True, exist_ok=True)

# def clone_pycefr_repository():
#     """
#     Clones the PyCEFR repository from GitHub.
#     """
#     if not Path(pycefr_dir).exists():
#         try:
#             subprocess.run(['git', 'clone', 'https://github.com/anapgh/pycefr.git', pycefr_dir], check=True)
#             print("PyCEFR repository cloned successfully.")
#         except subprocess.CalledProcessError as e:
#             print(f"Error cloning PyCEFR repository: {e}")
#     else:
#         print("PyCEFR repository already exists.")

# def run_pycefr_analysis():
#     """
#     Runs the PyCEFR analysis by executing its scripts and generating JSON data.
#     Attempts to continue execution even if an error occurs in subprocess calls.
#     """
#     original_dir = os.getcwd()
#     os.chdir(pycefr_dir)
    
#     scripts = [
#         ('python', 'dict.py'),
#         ('python', 'pycerfl.py', 'directory', '../PythonFiles')
#     ]
    
#     for script_command in scripts:
#         try:
#             subprocess.run(script_command, check=True)
#         except subprocess.CalledProcessError as e:
#             print(f"Error running {script_command[1]}: {e}. Continuing...")
    
#     os.chdir(original_dir)

# def process_json_files():
#     """
#     Processes JSON files generated by PyCEFR to extract competency levels and 
#     generate summary CSV and JSON files, excluding specific files.
#     """
#     exclude_files = ['repo_data.json', 'summary_data.json', 'total_data.json']  # Files to exclude

#     for json_file in Path(json_data_dir).glob('*.json'):
#         if json_file.name in exclude_files:
#             print(f"Skipping excluded file: {json_file.name}")
#             continue  # Skip this file and continue with the next

#         with open(json_file) as f:
#             data = json.load(f)

#         commit_hash = json_file.stem
#         all_files_data = data.get(commit_hash, {})
        
#         after_sum, before_sum = defaultdict(int), defaultdict(int)
        
#         for file_name, file_content in all_files_data.items():
#             parts = file_name.split('_')
#             if len(parts) < 6:
#                 print(f"Unexpected filename structure: {file_name}")
#                 continue
            
#             project_name = parts[1]
#             author_id = parts[2]
#             author_date_format = parts[3]
#             status = parts[4]
            
#             for level, score in file_content['Levels'].items():
#                 if 'after' in status:
#                     after_sum[level] += score
#                 elif 'before' in status:
#                     before_sum[level] += score
        
#         diff = {level: after_sum[level] - before_sum.get(level, 0) for level in set(after_sum) | set(before_sum)}
        
#         generate_summary_files(commit_hash, project_name, author_id, author_date_format, after_sum, before_sum, diff)

# def generate_summary_files(commit_hash, project_name, author_id, author_date_format, after_sum, before_sum, diff):
#     """
#     Generates CSV and JSON summary files for competency levels.
#     """
#     output_csv_dir = os.path.join(output_dir, 'CSV', project_name, author_id)
#     output_json_dir = os.path.join(output_dir, 'JSON', project_name, author_id)
#     Path(output_csv_dir).mkdir(parents=True, exist_ok=True)
#     Path(output_json_dir).mkdir(parents=True, exist_ok=True)

#     summary_base = f"{commit_hash}_summary_{author_date_format}"
#     csv_path = os.path.join(output_csv_dir, f"{summary_base}.csv")
#     json_path = os.path.join(output_json_dir, f"{summary_base}.json")

#     with open(csv_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['CommitHash', 'ProjectName', 'AuthorID', 'AuthorDateFormat', 'Level', 'After', 'Before', 'Difference'])
#         for level in sorted(set(after_sum.keys()).union(before_sum.keys())):
#             writer.writerow([
#                 commit_hash, project_name, author_id, author_date_format,
#                 level, after_sum.get(level, 0), before_sum.get(level, 0), diff.get(level, 0)
#             ])

#     with open(json_path, 'w') as jsonfile:
#         json.dump({
#             'CommitHash': commit_hash,
#             'ProjectName': project_name,
#             'AuthorID': author_id,
#             'AuthorDateFormat': author_date_format,
#             'Levels': {
#                 'After': dict(after_sum),
#                 'Before': dict(before_sum),
#                 'Difference': dict(diff)
#             }
#         }, jsonfile, indent=4)

# def main():
#     # Step 1: Clone PyCEFR repository
#     clone_pycefr_repository()

#     # Step 2: Run PyCEFR analysis
#     run_pycefr_analysis()
    
#     # Step 3: Process the JSON files to generate summaries
#     process_json_files()

#     print("Analysis and summary generation completed.")

# if __name__ == "__main__":
#     main()
# import subprocess
# import os
# import json
# import csv
# from collections import defaultdict
# from pathlib import Path

# # Define the directories
# pycefr_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\pycefr'  # Path to the PyCEFR scripts
# json_data_dir = os.path.join(pycefr_dir, 'DATA_JSON')  # Where JSON data will be stored
# output_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\CompetencyScore'  # Output directory for CSV and JSON files

# # Ensure output directory exists
# Path(output_dir).mkdir(parents=True, exist_ok=True)

# def clone_pycefr_repository():
#     """
#     Clones the PyCEFR repository from GitHub.
#     """
#     if not Path(pycefr_dir).exists():
#         try:
#             subprocess.run(['git', 'clone', 'https://github.com/anapgh/pycefr.git', pycefr_dir], check=True)
#             print("PyCEFR repository cloned successfully.")
#         except subprocess.CalledProcessError as e:
#             print(f"Error cloning PyCEFR repository: {e}")
#     else:
#         print("PyCEFR repository already exists.")

# def run_pycefr_analysis():
#     """
#     Runs the PyCEFR analysis by executing its scripts and generating JSON data.
#     Attempts to continue execution even if an error occurs in subprocess calls.
#     """
#     original_dir = os.getcwd()
#     os.chdir(pycefr_dir)
    
#     scripts = [
#         ('python', 'dict.py'),
#         ('python', 'pycerfl.py', 'directory', '../PythonFiles')
#     ]
    
#     for script_command in scripts:
#         try:
#             subprocess.run(script_command, check=True)
#         except subprocess.CalledProcessError as e:
#             print(f"Error running {script_command[1]}: {e}. Continuing...")
    
#     os.chdir(original_dir)

# def process_json_files():
#     """
#     Processes JSON files generated by PyCEFR to extract competency levels and 
#     generate summary CSV and JSON files, excluding specific files.
#     """
#     exclude_files = ['repo_data.json', 'summary_data.json', 'total_data.json']  # Files to exclude

#     for json_file in Path(json_data_dir).glob('*.json'):
#         if json_file.name in exclude_files:
#             print(f"Skipping excluded file: {json_file.name}")
#             continue  # Skip this file and continue with the next

#         with open(json_file) as f:
#             data = json.load(f)

#         commit_hash = json_file.stem
#         all_files_data = data.get(commit_hash, {})
        
#         after_sum, before_sum = defaultdict(int), defaultdict(int)
        
#         for file_name, file_content in all_files_data.items():
#             parts = file_name.split('_')
#             if len(parts) < 6:
#                 print(f"Unexpected filename structure: {file_name}")
#                 continue
            
#             project_name = parts[1]
#             author_id = parts[2]
#             author_date_format = parts[3]
#             status = parts[4]
            
#             for level, score in file_content['Levels'].items():
#                 if 'after' in status:
#                     after_sum[level] += score
#                 elif 'before' in status:
#                     before_sum[level] += score
        
#         diff = {level: after_sum[level] - before_sum.get(level, 0) for level in set(after_sum) | set(before_sum)}
        
#         generate_summary_files(commit_hash, project_name, author_id, author_date_format, after_sum, before_sum, diff, json_file.stem)

# def generate_summary_files(commit_hash, project_name, author_id, author_date_format, after_sum, before_sum, diff, file_stem):
#     """
#     Generates CSV and JSON summary files for competency levels.
#     """
#     output_csv_dir = os.path.join(output_dir, 'CSV', project_name, author_id)
#     output_json_dir = os.path.join(output_dir, 'JSON', project_name, author_id)
#     Path(output_csv_dir).mkdir(parents=True, exist_ok=True)
#     Path(output_json_dir).mkdir(parents=True, exist_ok=True)

#     summary_base = f"{file_stem}_summary_{author_date_format}"
#     csv_path = os.path.join(output_csv_dir, f"{summary_base}.csv")
#     json_path = os.path.join(output_json_dir, f"{summary_base}.json")

#     with open(csv_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['CommitHash', 'ProjectName', 'AuthorID', 'AuthorDateFormat', 'Level', 'After', 'Before', 'Difference'])
#         for level in sorted(set(after_sum.keys()).union(before_sum.keys())):
#             writer.writerow([
#                 commit_hash, project_name, author_id, author_date_format,
#                 level, after_sum.get(level, 0), before_sum.get(level, 0), diff.get(level, 0)
#             ])

#     with open(json_path, 'w') as jsonfile:
#         json.dump({
#             'CommitHash': commit_hash,
#             'ProjectName': project_name,
#             'AuthorID': author_id,
#             'AuthorDateFormat': author_date_format,
#             'Levels': {
#                 'After': dict(after_sum),
#                 'Before': dict(before_sum),
#                 'Difference': dict(diff)
#             }
#         }, jsonfile, indent=4)

# def main():
#     # Step 1: Clone PyCEFR repository
#     clone_pycefr_repository()

#     # Step 2: Run PyCEFR analysis
#     run_pycefr_analysis()
    
#     # Step 3: Process the JSON files to generate summaries
#     process_json_files()

#     print("Analysis and summary generation completed.")

# if __name__ == "__main__":
#     main()

import subprocess
import json
import csv
from collections import defaultdict
from pathlib import Path
import os

# Define the directories
# Default one in my desktop
# pycefr_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\pycefr'  # Path to the PyCEFR scripts
# json_data_dir = os.path.join(pycefr_dir, 'DATA_JSON')  # Where JSON data is stored
# output_dir = 'C:\\Users\\rujip\\Desktop\\SP_PyGress\\CompetencyScore'  # Output directory for CSV and JSON files

# mkdir -p /path/to/DATA_JSON
# mkdir -p /path/to/CompetencyScore
pycefr_dir = '/pycefr'  # Path to the PyCEFR scripts
json_data_dir = os.path.join(pycefr_dir, 'DATA_JSON')  # Where JSON data is stored
output_dir = '/CompetencyScore' 

# Ensure output directory exists
Path(output_dir).mkdir(parents=True, exist_ok=True)

def clone_pycefr_repository():
    """
    Clones the PyCEFR repository from GitHub.
    """
    if not Path(pycefr_dir).exists():
        try:
            subprocess.run(['git', 'clone', 'https://github.com/anapgh/pycefr.git', pycefr_dir], check=True)
            print("PyCEFR repository cloned successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning PyCEFR repository: {e}")
    else:
        print("PyCEFR repository already exists.")

def run_pycefr_analysis():
    """
    Runs the PyCEFR analysis by executing its scripts and generating JSON data.
    Attempts to continue execution even if an error occurs in subprocess calls.
    """
    original_dir = os.getcwd()
    os.chdir(pycefr_dir)
    
    scripts = [
        ('python', 'dict.py'),
        ('python', 'pycerfl.py', 'directory', '../PythonFiles_PyCEFR')
    ]
    
    for script_command in scripts:
        try:
            subprocess.run(script_command,check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script_command[1]}: {e}. Continuing...")
    
    os.chdir(original_dir)

def process_json_files():
    """
    Processes JSON files generated by PyCEFR to extract competency levels and 
    generate summary CSV and JSON files.
    """
    for json_file in Path(json_data_dir).glob('*.json'):
        process_json_file(json_file)

def process_json_file(json_file):
    """
    Processes a single JSON file generated by PyCEFR to extract competency levels and 
    generate summary CSV and JSON files.
    """
    with open(json_file) as f:
        data = json.load(f)

    commit_hash = json_file.stem
    all_files_data = data.get(commit_hash, {})
    
    after_sum, before_sum = defaultdict(int), defaultdict(int)
    
    for file_name, file_content in all_files_data.items():
        parts = file_name.split('_')
        if len(parts) < 7:  # Adjusted for time format inclusion
            print(f"Unexpected filename structure: {file_name}")
            continue
        
        project_name, author_id, author_date_format, time_format, status = parts[1], parts[2], parts[3], parts[4], parts[5]
        
        for level, score in file_content['Levels'].items():
            if 'after' in status:
                after_sum[level] += score
            elif 'before' in status:
                before_sum[level] += score
    
    diff = {level: after_sum[level] - before_sum.get(level, 0) for level in set(after_sum) | set(before_sum)}
    
    generate_summary_files(commit_hash, project_name, author_id, author_date_format, time_format, after_sum, before_sum, diff)

def generate_summary_files(commit_hash, project_name, author_id, author_date_format, time_format, after_sum, before_sum, diff):
    """
    Generates CSV and JSON summary files for competency levels, including time format.
    """
    output_csv_dir = os.path.join(output_dir, 'CSV', project_name, author_id)
    output_json_dir = os.path.join(output_dir, 'JSON', project_name, author_id)
    Path(output_csv_dir).mkdir(parents=True, exist_ok=True)
    Path(output_json_dir).mkdir(parents=True, exist_ok=True)

    summary_base = f"{commit_hash}_summary_{author_date_format}_{time_format}"
    csv_path = os.path.join(output_csv_dir, f"{summary_base}.csv")
    json_path = os.path.join(output_json_dir, f"{summary_base}.json")

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['CommitHash', 'ProjectName', 'AuthorID', 'AuthorDateFormat', 'TimeFormat', 'Level', 'After', 'Before', 'Difference'])
        for level in sorted(set(after_sum.keys()).union(before_sum.keys())):
            writer.writerow([
                commit_hash, project_name, author_id, author_date_format, time_format,
                level, after_sum.get(level, 0), before_sum.get(level, 0), diff.get(level, 0)
            ])

    with open(json_path, 'w') as jsonfile:
        json.dump({
            'CommitHash': commit_hash,
            'ProjectName': project_name,
            'AuthorID': author_id,
            'AuthorDateFormat': author_date_format,
            'TimeFormat': time_format,
            'Levels': {
                'After': dict(after_sum),
                'Before': dict(before_sum),
                'Difference': dict(diff)
            }
        }, jsonfile, indent=4)

def main():
    # Step 1: Clone PyCEFR repository
    clone_pycefr_repository()

    # Step 2: Run PyCEFR analysis
    run_pycefr_analysis()
    
    # Step 3: Process the JSON files to generate summaries
    process_json_files()

    print("Analysis and summary generation completed.")

if __name__ == "__main__":
    main()
