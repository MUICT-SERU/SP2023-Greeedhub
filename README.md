# PyGress

<br />

## File description 
#### ```requirement.txt```
- These libraries in this file are needed to install for conducting this project.  

#### ```PyDriller_ExtractData.py```
- Code for extracting GitHub Repo data using PyDriller.
- You need to include ``Project GitHub Repo URL`` and ``Project Name`` in the ```DataPyPI.csv```
* There are 2 sets of output: **GitHub Repo Data** and **Code before and after commit**
  * GitHub Repo Data can be found in ```PythonCommits_data/{ProjectName}_data.csv``` (1 row per 1 Commit)
  * Code before and after commit can be found in the directory ```PythonFiles/{ProjectName}``` -> Inside directories from here are grouped code from the same commit author's email (the author's email is hashed as the directory name). 

#### ```AnalyzeCompetencyScore.py```
* Main process for converting code from Project GitHub repo to PyCEFR Competency Score, which is divided into 7 steps
    * Step 1: Clone Repo ```PyCEFR```
    * Step 2: Create Directory ```CompetencyScore``` to store Competency Score from PyCEFR
    * Step 3: Create file ```filtered_all_projects.csv```
    * Step 4: Change Dir to PyCEFR
    * Step 5: Run dict.py to start the Competency Score extraction
    * Step 6: Analyze for tracking the status of each project whether that project is successfully extracted
    * Step 7: Calculate the competency score into sum A1 to C2 from each project
 * Set of Output 

 #### ```CalculateCompetencyScore.py```
 * This code is the Step 7 in ```AnalyzeCompetencyScore.py```
       
<br />

## How to run PyGress
### Step 0: Clone this repository
- ```git clone https://github.com/MUICT-SERU/SP2023-Greeedhub.git```

### Step 1: Install required libraries in ```requirements.txt```
- ```pip install -r requirements. txt```

### Step 2: Start Extract GitHub Data from listed repo using code from ```PyDriller_ExtractData.py```
- Start by running the code ```python PyDriller_ExtractData.py```
- Wait until all projects are extracted and stored in directories
- The result you will get from this step is code after and before commits from all projects in directory ```PythonFiles/{ProjectName}```
- Another result is the GitHub data in directory ```PythonCommits_data/{ProjectName}.csv``` (Metadata is coming soon) 

  --- Take a big break until all projects are extracted ---

### Step 3: Analyze GitHub Data and convert it to Competency Score list
- Running the code ```AnalyzeCompetencyScore.py```
- Wait until the Competency Score stores in the directory.
- The result you will get from this step is the list of all competency scores in each project in the directory ```CompetencyScore/{ProjectName}_CompetencyScore.csv``` (Metadata is coming soon) 
- Another result is the grouped list of competency scores (grouped by competency score A1 to C2 (As 6 grouped lists)), which is in the directory ```นั่นสิ ลืมแล้ว```
  
  --- Take another huge break until competency score from all projects are calculated ---  

<br />

## How to run the visualization
1. step 1
2. step 2
3. step 3

<br />

## Dataset
The dataset is now available in Google Drive [Data/Project_CompetencyScore].
