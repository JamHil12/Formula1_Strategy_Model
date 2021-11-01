The [data_lookups](https://github.com/JamHil12/Formula1_Strategy_Model/tree/master/tools/data_lookups) folder contains manually-made csv lookups that must be updated before running the tool.
For example, the tyre choices made by drivers during rach race must be defined. This information is sourced from Pirelli's website, e.g. https://racingspot.pirelli.com/global/en-ww/gp-hungary.

These csv files should be uploaded manually to the BigQuery project, using the naming convention and schemas in the table below. These BigQuery tables are what allow the 'combined' dataset to be created through the main download code. Without these manual lookups, there is no tyre usage data to combine with the Ergast API timing data.

In all of the entries in the table below, {YYYYRR} is replaced by the 4-digit year and 2-digit round number of the race for which the data is for.
| Dataset Name | Table Name | Description | Table Schema |
| ------------ | ----------- | ----------- | ----------- |
| Custom_Lookups  | Tyre_Stints_{YYYYRR} | The tyres used by each driver on which laps, according to the tyre manufacturer Pirelli's online data | year INTEGER; round INTEGER; driverId STRING; stint INTEGER; tyre STRING; tyre_description STRING; tyre_status STRING; from_lap INTEGER; to_lap INTEGER |
| Custom_Lookups  | Circuit_Ratings | Ratings from 1 to 5 of circuit characteristics, from the tyre manufacturer Pirelli | circuitId STRING; pirelli_url STRING; tyre_stress INTEGER; asphalt_abrasion INTEGER; asphalt_grip INTEGER; downforce INTEGER; lateral INTEGER |
