import os
import json

# Specify the base directory containing project folders
base_directory = r"C:\Users\Oily_brd\Desktop\Greeedhub\visualization_difference\CompetencyScore_Dead"

# Iterate over each project folder
for project_folder in os.listdir(base_directory):
    project_path = os.path.join(base_directory, project_folder)
    
    # Check if the item in the base directory is a folder
    if os.path.isdir(project_path):
        print(f"Processing project: {project_folder}")
        
        # Iterate over each JSON file in the project folder
        for file_name in os.listdir(project_path):
            # Check if the file is a JSON file
            if file_name.endswith('.json'):
                # Construct the full file path
                file_path = os.path.join(project_path, file_name)

                # Load JSON data
                with open(file_path, "r") as f:
                    data = json.load(f)

                # Modify the "Difference" values
                for level, value in data["Levels"]["Difference"].items():
                    if value < 0:
                        data["Levels"]["Difference"][level] = 0

                # Write the modified JSON data back to the file
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=4)

