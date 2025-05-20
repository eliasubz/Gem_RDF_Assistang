Experiment 2.1
Here we work with the curated dataset (Experiment 2) and try to find the overarching main entity (.1)


The experiment is being run in src/ecc_folder
First experiment went shit.
Masked files were useles because I only gave columns which means that they had zero real context but only masked column names. 
I got patients everywhere:
patient is apparently the default answer
Patients.csv because the columns have to do with patient information
lab results because the columns are just random four digit numbers 
diagnosis only has bullshit patient_id;id;code_snomed;date none of these names have to do with diagnosis. the only way would be to enrich the data with the real meaning of the snomed code.

Added preprocessing by adding snomed cd to natural language and added a couple of values. 