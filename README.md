# PyGress

<br />

## File description 
#### ```requirement.txt```
- These libraries are needed to install in this project.  

#### ```PyDriller_ExtractData.py```
- Code for extracting GitHub Repo data using PyDriller.
- You need to include ``Project GitHub Repo URL`` and ``Project Name`` in the ```DataPyPI.csv```
* There are 2 sets of output: **GitHub Repo Data** and **Code before and after commit**
  * GitHub Repo Data can be found in ```PythonCommits_data/{ProjectName}_data.csv``` (1 row per 1 Commit)
  * Code before and after commit can be found in directory ```PythonFiles/{ProjectName}```

#### ```AnalyzeCompetencyScore.py```
* Main process for converting code from Project GitHub repo to PyCEFR Competency Score, which is divided into 7 steps
    * Step 1: Clone Repo ```PyCEFR```
    * Step 2: Create Directory ```CompetencyScore``` to store Competency Score from PyCEFR
    * Step 3: Create file ```filtered_all_projects.csv```
    * Step 4: Change Dir to PyCEFR
    * Step 5: Run dict.py for starting Competency Score extraction
    * Step 6: Analyze for tracking status of each project whether that project is successfully extracted
    * Step 7: Calculate the competency score into sum A1 to C2 from each project
       
<br />

## How to run PyGress
### Step 0: Clone this repository
- ```git clone https://github.com/MUICT-SERU/SP2023-Greeedhub.git```

### Step 1: Install required libraries in ```requirements.txt```
- ```pip install -r requirements. txt```

### Step 2: Start Extract GitHub Data from listed repo using code from ```PyDriller_ExtractData.py```
- Start by running the code ```python 1_PyDriller_ExtractData.py```

### Step 3: 

<br />

## How to run the visualization
1. step 1
2. step 2
3. step 3

<br />

## Dataset
The dataset is now available in Google Drive [Data/Project_CompetencyScore].
