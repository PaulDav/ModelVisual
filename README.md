# Model Visual

This project takes a concept model and a logical model defined in a set of CSV files, and generates visualisations.

This has been used to define the SAVVI concept and logical models - see [SAVVI Concept Model](https://coda.io/@savvi/welcome/the-savvi-concept-model-21) and [SAVVI Logical Model](https://coda.io/@savvi/welcome/the-savvi-logical-model-22)

For the SAVVI example, the models are defined in a [google sheet](https://docs.google.com/spreadsheets/d/1v9dlS6dZaIJnvETSaWGWARgv9fhCkQEs-9qfvf9VA4k/edit?usp=sharing).  A CSV file is generated from each tab, and contained in the csv folder.


# Folders

## csv
The CSV files containing the definition of the models. 
* Concept Model.csv
* Logical Model.csv
* Data Structures.csv
* Terminology.csv
* Use Cases.csv


 
## graph_output
Having run the script, this folder then contains

### File types
* .gv files containing the dot script for graphviz
* .png files as images
* .svg files as images

### Files

* conceptModel - the concept model
* EntireEntityModel - the logical model

### sub folders
#### entity
A file for each entity in the logical model
#### use_cases
A file for each use case which shows only the entities neccessary

## csv_output

### Entity Attributes
A csv table for each entity listing its attribtues.

### Structure Attributes
a csv table for each data structure which can be used as a data type for any entity/attribute.

# To Run

* clear the output folders
* place the csv files that define the model in the csv folder
* adjust the last line of each python script to use the right name for the input csv file
* run the python script - runAll.py
* see the output in the output folders


# Requires python modules

graphviz 

` $ pip install graphviz`

# Requires GraphViz to be install on system path

Win10 `choco install graphviz`

Mac `brew install graphviz`

If error `Format: "svg" not recognized.` is returned run `dot -c` from an administrator terminal