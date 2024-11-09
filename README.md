# PyGress
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
1. **Clone the Repository**
   
   Clone this repository to your local machine: `git clone https://github.com/YourUsername/YourRepo.git`

2. **Install Required Dependencies**
   
   Navigate to the project directory and install the necessary Python libraries listed in requirements.txt: `pip install -r requirements.txt`

3. **Prepare Your Data**
   
   Place your JSON files containing competency levels data in the specified directory. Update the directory_path variable in the code files to match the location of your JSON files: `directory_path = r"C:\path\to\your\dataset"`

4. **Run the K-Means Clustering and Visualization Script**
   
   To perform K-Means clustering and generate visualizations.
- Load Data: Reads each JSON file and calculates competency percentages for each level.
- K-Means Clustering: Groups contributors into clusters (default k=7).
- Parallel Coordinates Plot: Creates a Parallel Coordinates plot for each cluster and centroid.
Run the following command: python your_kmeans_script.py

5. **View the Visualizations**

   Two interactive visualizations will be generated:
- Clusters Visualization: Shows contributors in a Parallel Coordinates plot, with colors representing clusters.
- Centroids Visualization: Displays cluster centroids on a separate Parallel Coordinates plot.
   Each plot allows you to explore competency distributions across contributors, with each competency level mapped to a separate axis.

<sub>**Note:**
Cluster Colors: Each cluster is color-coded.
Hover Data: Hover over each axis to view competency percentages for individual contributors or centroid clusters.</sub>

## Spider Chart and Slider Graph Visualization

The `visualization_Graph` folder contains the results of visualizing various competency score data. The folder is organized into five subfolders and 40 results in HTML files.

<sub>**Note:** All file paths and references within these HTML files are designed to be run locally on your machine.</sub>

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
