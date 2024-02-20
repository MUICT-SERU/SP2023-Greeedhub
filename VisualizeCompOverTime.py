import plotly.express as px
import pandas as pd
import numpy as np
import json
import os

# Get the current working directory
current_directory = os.getcwd()

# Specify the directory containing JSON files
directory_path = r"C:\Users\rujip\Desktop\SP2023-Greeedhub\CompetencyScore\JSON\pydriller"  # Update this path to your directory

# Verify directory path and list all JSON files in the directory
if os.path.exists(directory_path):
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
    print(f"Found {len(json_files)} JSON files.")
else:
    print(f"Directory does not exist: {directory_path}")
    json_files = []

# Initialize an empty list to store DataFrames from each file
dfs = []

# Check if JSON files were found
if not json_files:
    print("No JSON files found. Exiting script.")
    exit()

# Iterate over each JSON file
for file_name in json_files:
    # Construct the full file path
    file_path = os.path.join(directory_path, file_name)

    try:
        # Load JSON data
        with open(file_path, "r") as f:
            data = json.load(f)

        # Extracting the Levels data for the initial date
        initial_levels_data = data.get("Levels", {}).get("After", {})

        # Constructing the DataFrame for the initial date
        df = pd.DataFrame([
            {
                "Year": int(data["AuthorDateFormat"][:4]),
                "Month": int(data["AuthorDateFormat"][4:6]),
                "Day": int(data["AuthorDateFormat"][6:8]),
                "Level": level,
                "Value": initial_levels_data.get(level, 0)
            }
            for level in ["A1", "A2", "B1", "B2", "C1", "C2"]
        ])

        # Append the DataFrame to the list
        dfs.append(df)
    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

# Proceed only if there are DataFrames to concatenate
if dfs:
    final_df = pd.concat(dfs, ignore_index=True)

    # Sort the DataFrame by year and month
    final_df = final_df.sort_values(by=['Year', 'Month'])

    # Combine values for the same month and level
    final_df = final_df.groupby(['Year', 'Month', 'Level']).agg({'Value': 'sum'}).reset_index()

    # Apply logarithmic scaling to 'Value' to normalize the range across levels
    final_df['LogValue'] = np.log10(final_df['Value'] + 1)  # Adding 1 to avoid log(0)

    # Define the order of competency levels
    competency_order = ["A1", "A2", "B1", "B2", "C1", "C2"]

    # Add a column for level ordering
    level_order = {level: i for i, level in enumerate(competency_order)}
    final_df['LevelOrder'] = final_df['Level'].map(level_order)

    # Plotting
    fig = px.scatter(final_df, x='Month', y='LevelOrder', size='LogValue', color='Level',
                    labels={'LevelOrder': 'Competency Level', 'LogValue': 'Logarithmic Value'},
                    category_orders={'Month': list(range(1, 13)), 'LevelOrder': competency_order},
                    animation_frame='Year')

    fig.update_yaxes(tickvals=list(level_order.values()), ticktext=competency_order)

    fig.update_layout(
        title="Visualization of Developer’s Code Competency Over Time",
        xaxis=dict(title='Month', tickmode='array', tickvals=list(range(1, 13)),
                ticktext=['January', 'February', 'March', 'April', 'May', 'June',
                            'July', 'August', 'September', 'October', 'November', 'December']),
        yaxis=dict(title='Competency Level'),
        showlegend=True
    )

    # Adjusting marker sizes to be larger and more balanced across levels
    fig.update_traces(marker=dict(sizemode='area', sizeref=0.1, sizemin=4.0))

    fig.show()
else:
    print("No data to process. Please check the input files and directory path.")
