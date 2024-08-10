import plotly.graph_objects as go
import pandas as pd
import json
import os
from sklearn.cluster import KMeans

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
    initial_levels_data = data.get("Levels", {}).get("Difference", {})

    # Check if any value in the "Difference" is negative and replace it with 0
    for level, value in initial_levels_data.items():
        if value < 0:
            initial_levels_data[level] = 0
        # Calculate the total value for normalization
        total_value = sum(initial_levels_data.values())

    # Calculate the percentage for each level
    percentage_data = {}
    if total_value != 0:  # Check if total_value is not zero
        percentage_data = {level: (initial_levels_data.get(level, 0) / total_value) * 100 for level in ["A1", "A2", "B1", "B2", "C1", "C2"]}
        # print('percentage data: ', percentage_data)

    if all(initial_levels_data.get(level, 0) == 0 for level in ["A1", "A2", "B1", "B2", "C1", "C2"]):
        continue  # Skip this file

    # Constructing the DataFrame for the initial date
    df = pd.DataFrame([
        {
            "AuthorID": data["AuthorID"],
            "A1": percentage_data.get("A1", 0),
            "A2": percentage_data.get("A2", 0),
            "B1": percentage_data.get("B1", 0),
            "B2": percentage_data.get("B2", 0),
            "C1": percentage_data.get("C1", 0),
            "C2": percentage_data.get("C2", 0)
        }
    ])

    # Append the DataFrame to the list
    dfs.append(df)

# Concatenate all DataFrames into a single DataFrame
final_df = pd.concat(dfs, ignore_index=True)

# Perform K-Means clustering with 2 clusters
kmeans = KMeans(n_clusters=7, random_state=42)
cluster_labels = kmeans.fit_predict(final_df.drop('AuthorID', axis=1))


# Add cluster labels to the DataFrame
final_df['Cluster'] = cluster_labels
print('final_df: ', final_df['Cluster'])

# findind the cluster 0 in the final_df
cluster_0_data = final_df[final_df['Cluster'] == 0]
cluster_1_data = final_df[final_df['Cluster'] == 1]
cluster_2_data = final_df[final_df['Cluster'] == 2]

# Calculate cluster centroids
centroids = pd.DataFrame(kmeans.cluster_centers_, columns=final_df.drop(['AuthorID', 'Cluster'], axis=1).columns)

# Plot Parallel Coordinates Plot for clusters
fig_clusters = go.Figure(data=go.Parcoords(
 line=dict(color=final_df['Cluster'], colorscale=[[0, 'red'], [0.5, 'blue']]),
 dimensions=[
  dict(label='A1', values=final_df['A1'], range=[0, 100]),
  dict(label='A2', values=final_df['A2'], range=[0, 100]),
  dict(label='B1', values=final_df['B1'], range=[0, 100]),
  dict(label='B2', values=final_df['B2'], range=[0, 100]),
  dict(label='C1', values=final_df['C1'], range=[0, 100]),
  dict(label='C2', values=final_df['C2'], range=[0, 100])
 ]
))

# Update layout for clusters plot
fig_clusters.update_layout(
 title='Parallel Coordinates Plot for Clusters (Percentage ,K=2)',
 xaxis=dict(title='Competency Level'),
 yaxis=dict(title='Percentage'),
  showlegend=False
)

# Plot Parallel Coordinates Plot for clusters
fig_clusters = go.Figure(data=go.Parcoords(
line=dict(color=final_df['Cluster'], colorscale=[[0, 'red'], [0.14, 'orange'], [0.29, 'yellow'], [0.43, 'green'], [0.57, 'blue'], [0.71, 'purple'], [1, 'black']]),
 dimensions=[
  dict(label='A1', values=final_df['A1'], range=[0, 100]),
  dict(label='A2', values=final_df['A2'], range=[0, 100]),
  dict(label='B1', values=final_df['B1'], range=[0, 100]),
  dict(label='B2', values=final_df['B2'], range=[0, 100]),
  dict(label='C1', values=final_df['C1'], range=[0, 100]),
  dict(label='C2', values=final_df['C2'], range=[0, 100])
 ]
))

# Update layout for clusters plot
fig_clusters.update_layout(
 title='Parallel Coordinates Plot for Clusters (Percentage ,K=7)',
 xaxis=dict(title='Competency Level'),
 yaxis=dict(title='Percentage'),
  showlegend=False
)

# Plot Parallel Coordinates Plot for centroids
fig_centroids = go.Figure(data=go.Parcoords(
line=dict(color=centroids.index, colorscale=[[0, 'red'], [0.14, 'orange'], [0.29, 'yellow'], [0.43, 'green'], [0.57, 'blue'], [0.71, 'purple'], [1, 'black']]),
 dimensions=[
  dict(label='A1', values=centroids['A1'], range=[0, 100]),
  dict(label='A2', values=centroids['A2'], range=[0, 100]),
  dict(label='B1', values=centroids['B1'], range=[0, 100]),
  dict(label='B2', values=centroids['B2'], range=[0, 100]),
  dict(label='C1', values=centroids['C1'], range=[0, 100]),
  dict(label='C2', values=centroids['C2'], range=[0, 100])
 ]
))

# Update layout for centroids plot
fig_centroids.update_layout(
    title='Parallel Coordinates Plot for Centroids (Percentage ,K=7)',
    xaxis=dict(title='Competency Level'),
    yaxis=dict(title='Percentage')
)

# Show plots
fig_clusters.show()
fig_centroids.show()