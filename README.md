# Formula 1 Strategy Model
This was a 'weekend project' done in my spare time, to devise a simple model using Python to try to optimise a Formula 1 race strategy.

## Technical Requirements
All Python code was originally created using Python 3.7 (32 bit), using the packages available in the requirements.txt file.
To run any Jupyter notebooks, type 'jupyter lab' in the command line once the Python virtual environment is activated, to launch the JupyterLab interface.

## How to get started
1. Sign up to Google Cloud Platform (GCP) & create a Google BigQuery project. Create datasets in your BigQuery project called *"Custom_Lookups"*, *"F1_Modelling_Raw"* and *"F1_Modelling_Combined"*, which will store all the data you process.
2. Create a service account which has access to the BigQuery project, and store the json file for the service account's credentials in the folder *"credentials"*
3. Amend the Python files in  the *"python_..."* folders so that any reference to key_path points to the path of the json file retrieved in step 2
4. Choose a particular race, and manually collect tyre stint data from Pirelli's site, e.g. via . Use the template csvs available in data/manual_lookups as an example. Once completed, these csvs should also be uploaded into BigQuery, manually into a dataset called *"Custom_Lookups"*.
5. Go to *"python_Upload/Upload__Master.py"*, enter a year, start and end round number, as well as what type of data you want to upload. Running this will download all the key datasets (drivers, constructors, race laptimes, pitstops, qualifying laptimes etc) from the Ergast API, and store them in the *"F1_Modelling_Raw"* dataset in BigQuery. If you select to also upload combined data, then it will use the manual lookups from step 4 to merge the tyre stint data with the Ergast data, and store the complete combined dataset in *"F1_Modelling_Combined"* in BigQuery.
6. Finally, go to *"python_Modelling/Modelling__Master.py"* which can be used to call the various race strategy models.

## Folders in this Git repository
| Folder Name  | Description |
| ------------ | ----------- |
| credentials  | In here you should store the json file for your Google BigQuery credentials, for the project in which you want to store all your results.  |
| data  | Contains manual lookup csv files which can be manually uploaded into BigQuery to supplement the data from the Ergast API. For example, tyre stint data can be manually collected and uploaded. | 
| python_Modelling | In here are all the Python files needed to call the optimal strategy models, plot laptimes and perform grid search optimisation across different modelling parameters. The file 'Modelling__Master.py' should be used in the first instance; this calls all the other files in one run. |
| python_Upload | In here are all the Python files needed to call the Ergast API and store the results into Google BigQuery. The file 'Upload__Master.py' should be used in the first instance; this calls all the other files in one run. |
