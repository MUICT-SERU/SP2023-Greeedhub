import plotly.express as px
import pandas as pd
import json
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

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
    initial_levels_data = data.get("Levels", {}).get("After", {})

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

# Pivot the DataFrame to have competency levels as columns and each row representing a contributor
pivot_df = final_df.pivot_table(index='AuthorID', columns='Level', values='Value', aggfunc='sum', fill_value=0).reset_index()

# Count the number of projects each contributor has worked on
contributor_projects = final_df.groupby('AuthorID')['Year'].nunique().reset_index()
contributor_projects.columns = ['AuthorID', 'Projects']

# Merge the project count with the pivot DataFrame
pivot_df = pd.merge(pivot_df, contributor_projects, on='AuthorID', how='left')

# Apply PCA for dimensionality reduction
pca = PCA(n_components=2)
pca_data = pca.fit_transform(pivot_df.drop(['AuthorID', 'Projects'], axis=1))

# Perform K-Means clustering
kmeans = KMeans(n_clusters=7, random_state=42)
cluster_labels = kmeans.fit_predict(pca_data)

# Add cluster labels to the DataFrame
pivot_df['Cluster'] = cluster_labels
pivot_df['Cluster'] = pivot_df['Cluster'].astype(str)

# Define hover data including all necessary columns
hover_data = ['AuthorID', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Projects', 'Cluster']

# Define a dictionary to map cluster labels to colors
cluster_colors = {'0': 'red', '1': 'blue', '2': 'green', '3': 'yellow', '4': 'orange', '5': 'purple', '6': 'black'}

# Plot the K-Means clustering results with custom colors and legend order
fig = px.scatter(pivot_df, x=pca_data[:, 0], y=pca_data[:, 1], color='Cluster', size='Projects', hover_data=hover_data, 
                 title='K-Means Clustering of Contributors (Raw Value, K=7)', labels={'x': 'PCA Component 1', 'y': 'PCA Component 2'},
                 color_discrete_map=cluster_colors, category_orders={'Cluster': ['0', '1', '2', '3', '4', '5', '6']})
fig.show()
