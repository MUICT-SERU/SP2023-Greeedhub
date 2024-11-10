# PyGress

## File description 
#### ```requirement.txt```
- These libraries in this file are needed to install for conducting this project.  

#### ```PyDriller_ExtractData.py```
- Code for extracting GitHub Repo data using PyDriller.
- You need to include ``Project GitHub Repo URL`` and ``Project Name`` in the ```DataPyPI.csv```.
* There are 2 sets of output: **GitHub Repo Data** and **Code before and after commit**.
  * GitHub Repo Data can be found in ```PythonCommits_data/{ProjectName}_data.csv``` (1 row per 1 Commit).
  * Code before and after commit can be found in the directory ```PythonFiles/{ProjectName}``` -> Inside directories from here are grouped code from the same commit author's email (the author's email is hashed as the directory name). 

#### ```AnalyzeCompetencyScore.py```
* Main process for converting code from Project GitHub repo to PyCEFR Competency Score, which is divided into 7 steps.
    * Step 1: Clone Repo ```PyCEFR```
    * Step 2: Create Directory ```CompetencyScore``` to store Competency Score from PyCEFR
    * Step 3: Create file ```filtered_all_projects.csv```
    * Step 4: Change Dir to PyCEFR
    * Step 5: Run dict.py to start the Competency Score extraction
    * Step 6: Analyze for tracking the status of each project whether that project is successfully extracted
    * Step 7: Calculate the competency score into sum A1 to C2 from each project

 #### ```CalculateCompetencyScore.py```
 * This code is the Step 7 in ```AnalyzeCompetencyScore.py```.
       
<br />

# ➡ Main Step 1: How to get Competency Score
###  Step 0: Clone this repository
- Command script ```git clone https://github.com/MUICT-SERU/SP2023-Greeedhub.git```
  <br></br>
###  Step 1: Install required libraries in ```requirements.txt```
- Command script ```pip install -r requirements.txt```
  <br></br>
###  Step 2: Start Extract GitHub Data from listed repo using code from ```PyDriller_ExtractData.py```
- Start by running the script ```python PyDriller_ExtractData.py```
- Wait until all projects are extracted and stored in directories
- The result you will get from this step is code after and before commits from all projects in the directory ```PythonFiles/{ProjectName}```
- Another result is the GitHub data in directory ```PythonCommits_data/{ProjectName}.csv``` (Metadata is coming soon) 

  --- Take a big break until all projects are extracted ---
  <br></br>
###  Step 3: Analyze GitHub Data and convert it to the Competency Score list
- Running the code ```AnalyzeCompetencyScore.py```
- Wait until the Competency Score stores in the directory.
- The result you will get from this step is the list of all competency scores in each project in the directory ```CompetencyScore/{ProjectName}_CompetencyScore.csv``` (Metadata is coming soon) 
- Another result is the grouped list of competency scores (grouped by competency score A1 to C2 as 6 grouped lists).
  
  --- Take another huge break until the competency score from all projects are calculated ---  
<br />

# ➡ Main Step 2: How to run the visualization
## K-Means Clustering and Parallel Coordinates Visualization

### Folder Structure
1. **K-Means Clustering**

   K-means folder contains `K-means.py`. This script applies K-Means clustering to contributor data based on their competency levels (A1 to C2). It groups contributors into clusters by similarity in skill levels, calculated as percentages for each level from A1 to C2. Clustered data is visualized with cluster labels assigned to each contributor as a result. In addition, the cluster's number of this file is set to 7 (K=7) by default (if you want to change, you can modify the number).

2. **Parallel Coordinates Visualization**
   Parallel folder contains `parallel_raw_k7.py`. This script generates Parallel Coordinates plots for visualizing contributors' competency scores across all levels (A1 to C2) and their associated centroids. It displays clusters and centroids on parallel axes, with each axis representing a specific competency level.
There are two visualizations as outputs:
- A Parallel Coordinates plot for individual contributors within clusters.
- A Parallel Coordinates plot for centroids, showing the average competency level across clusters.

### How to run

### Step 1: Run the K-Means Clustering and Visualization Script
- To perform K-Means clustering and generate visualizations.
- Load Data: Reads each JSON file and calculates competency percentages for each level.
- K-Means Clustering: Groups contributors into clusters (default k=7).
- Parallel Coordinates Plot: Creates a Parallel Coordinates plot for each cluster and centroid. Run the following command: python your_kmeans_script.py
<br></br>

### Step 2: View the Visualizations
   Two interactive visualizations will be generated:
- Clusters Visualization: Shows contributors in a Parallel Coordinates plot, with colors representing clusters.
- Centroids Visualization: Displays cluster centroids on a separate Parallel Coordinates plot.
   Each plot allows you to explore competency distributions across contributors, with each competency level mapped to a separate axis.
  <br></br>
  <sub> **Note:** </sub>
  <sub> - Cluster Colors: Each cluster is color-coded </sub>
  <sub> - Hover Data: Hover over each axis to view competency percentages for individual contributors or centroid clusters.</sub>
  
## Spider Chart and Slider Graph Visualization
- The `visualization_Graph` folder contains the results of visualizing various competency score data. The folder is organized into five subfolders and 40 results in HTML files.
- **Note:** All file paths and references within these HTML files are designed to be run locally on your machine.

### Folder Structure

1. **change_to_zero**  
   This folder contains the code to modify the competency scores (dataset). Any negative differences in the scores have been changed to zero. This adjustment applies to both `CompetencyScore_Alive` and `CompetencyScore_Dead`.

   **To run change_to_zero_Alive and change_to_zero_Dead**
   
   Just "Run Python File"

3. **CompetencyScore_Alive**  
   This folder holds the results after applying the changes made in the `change_to_zero` folder. It contains the adjusted competency scores for the 20 "Alive" projects.

4. **CompetencyScore_Dead**  
   Similar to the `CompetencyScore_Alive` folder, this one contains the results after applying the changes made in the `change_to_zero` folder. It contains the adjusted competency scores for the 20 "Dead" projects.

5. **Visualize_Alive_project**  
   This folder contains 20 Python files that generate visualization graphs for the "Alive" category.

   **To run each file in Visualize_Alive_project**
   
   Just "Run Python File"

7. **Visualize_Dead_project**  
   Similar to the `Visualize_Alive_project` folder. This folder contains 20 Python files that generate visualization graphs for the "Dead" category.

   **To run each file in Visualize_Alive_project**
   
   Just "Run Python File"

9. **40 results in HTML files**
   There are 40 results in HTML files from Visualize_Alive_project and Visualize_Dead_project folder. The visualizations include a spider chart and a slider graph of overall project, and spider charts and slider graphs of each contributor.

   **To run change_to_zero_Alive and change_to_zero_Dead**
   
   Click "Run" --> "Start Debugging" --> and choose Web App to visualize the result, such as Chrome or Edge

## Dataset
The dataset is now available in Google Drive [Data/Project_CompetencyScore].
