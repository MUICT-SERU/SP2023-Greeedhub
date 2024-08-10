import os
import json
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Specify the directory containing JSON files
directory_path = r"\Users\username\projects\my-app"

# List all JSON files in the directory
json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]

# Initialize an empty list to store DataFrames from each file
dfs = []

# Iterate over each JSON file
for file_name in json_files:
    # Construct the full file path
    file_path = os.path.join(directory_path, file_name)

    # Load JSON data
    with open(file_path, "r") as f:
        data = json.load(f)

    # Extracting the Levels data for the initial date
    initial_levels_data = data.get("Levels", {}).get("Differece", {})

    # Check if all competency levels are 0
    if all(value == 0 for value in initial_levels_data.values()):
        continue  # Skip this file

    # Constructing the DataFrame for the initial date
    df = pd.DataFrame([
        {
            "Year": int(data["AuthorDateFormat"][:4]),
            "Month": int(data["AuthorDateFormat"][4:6]),
            "Day": int(data["AuthorDateFormat"][6:8]),
            "Level": level,
            "Value": initial_levels_data.get(level, 0),
            "AuthorID": data["AuthorID"]
        }
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]
    ])

    # Append the DataFrame to the list
    dfs.append(df)

# Concatenate all DataFrames into a single DataFrame
final_df = pd.concat(dfs, ignore_index=True)

# Sort the DataFrame by year, month, day, and author ID
final_df = final_df.sort_values(by=['Year', 'Month', 'Day', 'AuthorID'])

# Combine values for the same year, month, day, level, and author ID
final_df = final_df.groupby(['Year', 'Month', 'Day', 'Level', 'AuthorID']).agg({'Value': 'sum'}).reset_index()

# Calculate the total value for each group
final_df['Total'] = final_df.groupby(['Year', 'Month', 'Day', 'AuthorID'])['Value'].transform('sum')

# Calculate the percentage and round to 2 decimal places
final_df['Percentage'] = ((final_df['Value'] / final_df['Total']) * 100).round(2)

# Pivot the DataFrame to have competency levels as columns and each row representing a contributor
pivot_df = final_df.pivot_table(index='AuthorID', columns='Level', values='Percentage', fill_value=0).reset_index()

# Count the number of projects each contributor has worked on
contributor_projects = final_df.groupby('AuthorID')['Year'].nunique().reset_index()
contributor_projects.columns = ['AuthorID', 'Projects']

# Merge the project count with the pivot DataFrame
pivot_df = pd.merge(pivot_df, contributor_projects, on='AuthorID', how='left')

# Scale the original data
scaler = StandardScaler()
scaled_data_original = scaler.fit_transform(pivot_df.drop(['AuthorID', 'Projects'], axis=1))

# Implement the Elbow Method
cost = []
for k in range(1, 31):
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(scaled_data_original)
    cost.append(kmeans.inertia_)

# Plot the elbow curve
plt.plot(range(1, 31), cost, marker='o', linestyle='--', color='b')
plt.xlabel('Number of clusters (K)')
plt.ylabel('Sum of squared distances')
plt.title('Elbow Method for Optimal K')
plt.show()
