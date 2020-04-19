This folder contains manually-made csv lookups, e.g. of tyre choices made by drivers from actual F1 Grand Prix. This information is sourced from Pirelli's website, e.g. https://racingspot.pirelli.com/global/en-ww/gp-hungary.

These csv files should be uploaded to the BigQuery project, using the naming convention below. These tables are what allow the 'combined' dataset to be created through the main download code; without these manual lookups we don't have any tyre usage data to combine with the Ergast API data.
