import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os

# Get the current working directory
current_directory = os.getcwd()

# Specify the directory containing JSON files
directory_path = r"C:\Users\Oily_brd\Desktop\Greeedhub\visualization_difference\CompetencyScore_Alive\cloudmesh-common"  # Replace with your actual directory path

# Get the project name from the directory path
project_name = os.path.basename(directory_path)

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

    # Constructing the DataFrame for the initial date
    df = pd.DataFrame([
        {
            "Year": int(data["AuthorDateFormat"][:4]),
            "Month": int(data["AuthorDateFormat"][4:6]),
            "Day": int(data["AuthorDateFormat"][6:8]),
            "Level": level,
            "Value": max(initial_levels_data.get(level, 0), 0),  # Change negative values to 0
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

# Define the order of competency levels
competency_order = ["A1", "A2", "B1", "B2", "C1", "C2"]

# Calculate the total value for each group
final_df['Total'] = final_df.groupby(['Year', 'Month', 'Day', 'AuthorID'])['Value'].transform('sum')

# Rest of the code remains the same for plotting
level_order = {level: i for i, level in enumerate(competency_order)}
final_df['LevelOrder'] = final_df['Level'].map(level_order)

# Calculate the total value for each author
author_totals = final_df.groupby(['AuthorID'])['Value'].sum().reset_index()

# Define the radial axis range for the spider chart
spider_chart_range = [0, 100]

# Initialize an empty list to store HTML content
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<title>{project_name}</title>
</head>
<body>
<h1 style="text-align: center;">{project_name}</h1>
"""

# Create an overall spider chart with filled areas for each author
fig_spider_overall = go.Figure()

for author_id, author_data in final_df.groupby('AuthorID'):
    fig_spider_overall.add_trace(go.Scatterpolar(
        r=(author_data.groupby('Level')['Value'].sum() / author_totals[author_totals['AuthorID'] == author_id]['Value'].values[0] * 100).tolist(),
        theta=competency_order,
        fill='toself',
        name=f"AuthorID: {author_id}"
    ))

fig_spider_overall.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=spider_chart_range  # Set the radial axis range
        )
    ),
    title="Visualization of Overall Commits"
)

# Convert overall spider chart to HTML and append to HTML content
html_content += fig_spider_overall.to_html(full_html=False, include_plotlyjs='cdn')

# Create a slider chart for all commits of the project
fig_slider_overall = px.scatter(final_df, x='Month', y='LevelOrder', size='Value', color='Level',
                        labels={'LevelOrder': 'Competency Level', 'Value': 'Value'},
                        category_orders={'Month': list(range(1, 13)), 'LevelOrder': competency_order},
                        animation_frame='Year', range_x=[0.5, 12.5], range_y=[-0.5, len(competency_order)-0.8],
                        title="Visualization of Overall Commits",
                        hover_data={'AuthorID': True})  # Include AuthorID in hover data

fig_slider_overall.update_layout(
    xaxis=dict(title='Month', tickmode='array', tickvals=list(range(1, 13)),
               ticktext=['January', 'February', 'March', 'April', 'May', 'June',
                         'July', 'August', 'September', 'October', 'November', 'December']),
    yaxis=dict(title='Competency Level', tickmode='array', tickvals=list(range(len(competency_order))),
               ticktext=competency_order),
    showlegend=True,
    height=420,  # Adjust the height of the plot
    margin=dict(l=30, r=40, t=40, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)  # Align legend horizontally at the bottom
)

fig_slider_overall.update_traces(marker=dict(sizemode='area', sizeref=2.5 * max(final_df['Value']) / (50 ** 2)))  # Adjust the sizeref value

# Convert overall slider chart to HTML and append to HTML content
html_content += fig_slider_overall.to_html(full_html=False, include_plotlyjs='cdn')

# Loop through each author
for author_id in author_totals['AuthorID']:
    # Filter the data for the current author
    author_data = final_df[final_df['AuthorID'] == author_id]
    
    # Create a spider chart for the total percentage of code competency for the current author
    fig_spider = go.Figure()
    
    fig_spider.add_trace(go.Scatterpolar(
        r=(author_data.groupby('Level')['Value'].sum() / author_totals[author_totals['AuthorID'] == author_id]['Value'].values[0] * 100).tolist(),
        theta=competency_order,
        fill='toself',
        name=f"AuthorID: {author_id}"
    ))

    fig_spider.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=spider_chart_range  # Set the radial axis range
            )
        ),
        title=f"Visualization of Developer’s Code Competency - AuthorID: {author_id}",
        showlegend=True
    )

    # Add a box to cover the details with a buttermilk color
    fig_spider.add_shape(
        type="rect",
        xref="paper",
        yref="paper",
        x0=0,
        y0=0,
        x1=0.15,  # Adjust as needed
        y1=1,
        fillcolor="rgb(253, 245, 230)",  # Buttermilk color
        opacity=1,
        layer="below",
        line=dict(width=0)
    )

    # Calculate the horizontal position for the title to be in the center of the box
    title_x_pos = (0 + 0.15) / 2

    # Add title
    fig_spider.add_annotation(
        x=title_x_pos, y=1.02,  # Adjust position as needed
        xref='paper', yref='paper',
        text="Competency Levels",
        font=dict(size=14),
        showarrow=False,
        xanchor='center'  # Align title to the center
    )
    # Add annotation for each level score inside the box
    for level in competency_order[::-1]:  # Reverse the order of competency_order
        value = author_data.loc[author_data['Level'] == level, 'Value'].sum()
        y_pos = (len(competency_order) - 1 - competency_order.index(level)) / len(competency_order)  # Calculate y position in reverse order
        fig_spider.add_annotation(
            x=0.01,  # Adjusted x-coordinate to be inside the box on the left
            y=y_pos,
            text=f"{level}: {value}",
            showarrow=False,
            font=dict(size=12),
            xanchor="left"  # Align text to the left within the box
        )

    # Convert spider chart to HTML and append to HTML content
    html_content += fig_spider.to_html(full_html=False, include_plotlyjs='cdn')

    # Build the title with or without the year based on unique years
    title = f"Visualization of Developer’s Code Competency - AuthorID: {author_id}"
    unique_years = author_data['Year'].nunique()
    if unique_years == 1:
        title += f" - Year: {author_data['Year'].iloc[0]}"

    # Create a slider chart
    fig_slider_contributor = px.scatter(author_data, x='Month', y='LevelOrder', size='Value', color='Level',
                            labels={'LevelOrder': 'Competency Level', 'Value': 'Value'},
                            category_orders={'Month': list(range(1, 13))},
                            animation_frame='Year', range_x=[0.5, 12.5], range_y=[-0.5, len(competency_order)-0.8],
                            title=title)

    fig_slider_contributor.update_layout(
        xaxis=dict(title='Month', tickmode='array', tickvals=list(range(1, 13)),
                   ticktext=['January', 'February', 'March', 'April', 'May', 'June',
                             'July', 'August', 'September', 'October', 'November', 'December']),
        yaxis=dict(title='Competency Level', tickmode='array', tickvals=list(range(len(competency_order))),
                   ticktext=competency_order),
        showlegend=True,
        height=420,  # Adjust the height of the plot
        margin=dict(l=30, r=40, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)  # Align legend horizontally at the bottom
    )

    fig_slider_contributor.update_traces(marker=dict(sizemode='area', sizeref=2.5 * max(author_data['Value']) / (50 ** 2)))  # Adjust the sizeref value

    # Convert slider chart to HTML and append to HTML content
    html_content += fig_slider_contributor.to_html(full_html=False, include_plotlyjs='cdn')

# Add closing tags for HTML body and document
html_content += """
</body>
</html>
"""

# Save the HTML content to a file
file_name = f"A_{project_name}_visualization.html"
with open(file_name, "w") as f:
    f.write(html_content)
