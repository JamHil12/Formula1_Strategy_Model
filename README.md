# Formula 1 Strategy Model
### *Developer: Jamie Hilton*
This was a 'weekend project' done in Jamie Hilton's spare time, to devise a simple model using Python to try to optimise a Formula 1 race strategy.

## Acknowledgements
This project relies on the historial F1 datasets that are publically available via the Ergast API - for documentation please refer to http://ergast.com/mrd/. \
It also relies on data publically available from F1's sole tyre manufacturer Pirelli, for manual collection of tyre stint and circuit characteristics data.

## Technical Requirements
You will need:\
(a) a Google Cloud Platform (GCP) account and Google BigQuery project, which will store all the datasets used in the modelling\
(b) Python, with which all the models are based. All Python code was originally created using Python 3.7 (32 bit), and all the packages needed are available in the requirements.txt file for ease of setting up the Python environment.\
To run any Jupyter notebooks, type 'jupyter lab' in the command line once the Python virtual environment is activated, to launch the JupyterLab interface.

## How to get started
1. Create datasets in your newly BigQuery project called *"Custom_Lookups"*, *"F1_Modelling_Raw"* and *"F1_Modelling_Combined"*, which will store all the data you need for this model.
2. Create a service account which has access to the BigQuery project, and store the json file for the service account's credentials in the *"credentials"* folder(s).  As of April 2020, the area to create and manage service accounts is accessible via 'IAM & Admin' -> 'Service Accounts' in the GCP user interface.
3. Go to the *download* folder and follow the instructions in the README.md file to gather historical F1 Grand Prix data
4. Go to the *modelling* folder and follow the instructions in the README.md file to run strategy optimisation models

## Folders in this Git repository
| Folder Name  | Description |
| ------------ | ----------- |
| download | In here are all the Python files needed to call the Ergast API and store the results into Google BigQuery. |
| modelling | In here are all the Python files needed to call the optimal strategy models, plot laptimes and perform grid search optimisation across different modelling parameters. |
