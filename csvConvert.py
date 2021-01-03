import os
import csv


class csvConvert:
    def __init__(self, filepath_logical_model, filepath_concept_model, filepath_data_structures, filepath_terminology,
                 filepath_use_case):
        self.FilePathLogicalModel = filepath_logical_model
        self.FileConceptModel = filepath_concept_model
        self.FileDataStructure = filepath_data_structures
        self.FileTerminology = filepath_terminology
        self.FileUseCase = filepath_use_case
        self.port_id = 0
        self.concepts = self.generate_concepts()
        self.conceptsOf = self.generate_concepts_of()
        self.conceptOfEntity = {}
        self.entities = self.generate_entities()
        self.structures = self.generate_data_structures()
        self.use = self.generate_use_cases()
        # self.terminology = self.generate_terminology()
        self.convert_concepts()
        self.convert_entities()

    def generate_concepts(self) -> dict:
        """
        Converts the CSV into a dict while added multiple relationships to a single concept
        """
        with open(self.FileConceptModel, "r", errors="REPLACE") as file_concept_model:
            csv_file_concept = csv.DictReader(file_concept_model)
            previous_row = {}
            concepts = {}
            for row in csv_file_concept:
                if previous_row == {} or row["Concept"] != '':
                    previous_row = row

                    concepts[row["Concept"]] = {"Concept": row["Concept"],
                                                "Label": row["Label"] if row["Label"] else strip_savvi(
                                                    row["Concept"]),
                                                "Sub Class of": row["Sub Class of"],
                                                "Definition": row["Definition"],
                                                "Note - how is this used in SAVVI?": row[
                                                    "Note - how is this used in SAVVI?"], "Sources": row["Sources"],
                                                "Relationship": [], "Open Referral UK": row["Open Referral UK"]}
                    if row["Relationship"]:
                        concepts[row["Concept"]]["Relationship"].append({"Relationship": row["Relationship"],
                                                                         "Object": row["Object"]})
                else:
                    if row["Relationship"]:
                        concepts[previous_row["Concept"]]["Relationship"].append(
                            {"Relationship": row["Relationship"],
                             "Object": row["Object"]})
        return concepts

    def generate_concepts_of(self) -> dict:
        concepts_of = {}
        with open(self.FileConceptModel, "r", errors="REPLACE") as file_concept_model:
            csv_file_concept = csv.DictReader(file_concept_model)

            for row in csv_file_concept:
                if row["Concept"] != '':
                    concepts_of[row["Concept"]] = []

        with open(self.FileConceptModel, "r", errors="REPLACE") as file_concept_model:
            csv_file_concept = csv.DictReader(file_concept_model)
            previous_row = {}

            for row in csv_file_concept:
                if previous_row == {} or row["Concept"] != '':
                    previous_row = row
                    if row["Object"]:
                        concepts_of[row["Object"]].append(
                            {"Object": row["Object"], "Relationship": row["Relationship"],
                             "Concept": row["Concept"], "Label": row["Label"]})
                else:
                    if row["Object"]:
                        concepts_of[row["Object"]].append(
                            {"Object": row["Object"], "Relationship": row["Relationship"],
                             "Concept": previous_row["Concept"],
                             "Label": previous_row["Label"]})

        return concepts_of

    def generate_entities(self) -> dict:
        entities = {}

        with open(self.FilePathLogicalModel, "r", errors="REPLACE") as file_logical_model:
            csv_file_models = csv.DictReader(file_logical_model)
            previous_row = {}
            for row in csv_file_models:
                if previous_row == {} or row["Entity"] != '':
                    previous_row = row

                    entities[row["Entity"]] = {"Entity": row["Entity"], "Concept": [],
                                               "Concept Description": row["Concept Description"],
                                               "Entity Description": row["Entity Description"], "Attributes": [],
                                               "Source": row["Source"]}

                    if row["Concept"]:
                        entities[row["Entity"]]["Concept"].append(row["Concept"])
                        self.conceptOfEntity[row["Concept"]] = row["Entity"]

                    if row["Attributes"]:
                        entities[row["Entity"]]["Attributes"].append(
                            {"Attributes": row["Attributes"], "Description": row["Description"],
                             "Field Type": row["Field Type"], "Data Structure": row["Data Structure"],
                             "Occurs": row["Occurs"], "Required": row["Required"],
                             "Permitted Values": row["Permitted Values"]})
                else:
                    if row["Concept"]:
                        entities[previous_row["Entity"]]["Concept"].append(row["Concept"])
                        self.conceptOfEntity[row["Concept"]] = previous_row["Entity"]

                    if row["Attributes"]:
                        entities[previous_row["Entity"]]["Attributes"].append(
                            {"Attributes": row["Attributes"], "Description": row["Description"],
                             "Field Type": row["Field Type"], "Data Structure": row["Data Structure"],
                             "Occurs": row["Occurs"], "Required": row["Required"],
                             "Permitted Values": row["Permitted Values"]})

        return entities

    def generate_data_structures(self) -> dict:
        data = {}
        with open(self.FileDataStructure, "r", errors="REPLACE") as file_data_structure:
            csv_data_structure = csv.DictReader(file_data_structure)
            previous_row = {}
            for row in csv_data_structure:
                if row["Structure"] == "" and row["Attributes"] == "":
                    continue
                if previous_row == {} or row["Structure"] != '':
                    previous_row = row
                    if row["Attributes"]:
                        data[row["Structure"]] = [
                            {"Attribute": row["Attributes"], "Type": row["Field Type"], "Occurs": row["Occurs"]}]
                    else:
                        data[row["Structure"]] = []
                else:
                    if row["Attributes"]:
                        data[previous_row["Structure"]].append(
                            {"Attribute": row["Attributes"], "Type": row["Field Type"], "Occurs": row["Occurs"]})

        return data

    def generate_use_cases(self) -> dict:
        data = {}
        with open(self.FileUseCase, "r", errors="REPLACE") as file_use_case:
            csv_use_cases = csv.DictReader(file_use_case)
            previous_row = {}
            for row in csv_use_cases:
                if row["Concepts"] == "" and row["Entities"] == "":
                    continue
                if previous_row == {} or row["Use Case"] != '':
                    previous_row = row
                    if row["Concepts"]:
                        data[row["Use Case"]] = {"Concepts": [row["Concepts"]], "Entities": [row["Entities"]]}

                else:
                    if row["Concepts"]:
                        data[previous_row["Use Case"]]["Concepts"].append(row["Concepts"])
                    if row["Entities"]:
                        data[previous_row["Use Case"]]["Entities"].append(row["Entities"])

        return data

    def convert_concepts(self):
        headings = ["Concept", "Label", "Definition", "Smart City Concept Model"]

        with open(os.path.join(os.path.dirname(__file__), 'csv_output', 'Concepts.csv'), "w", newline='') as file_output:
            csv_output = csv.DictWriter(file_output, fieldnames=headings)
            csv_output.writeheader()

            for key, item in self.concepts.items():
                row = {"Concept": item["Concept"], "Label": str(item["Label"]).replace("\\n", " "),
                       "Definition": item["Definition"], "Smart City Concept Model": item["Sub Class of"]}
                csv_output.writerow(row)

    def convert_entities(self):
        headings = ["Entity", "Concept", "Description", "Source"]

        with open(os.path.join(os.path.dirname(__file__), 'csv_output', 'Entities.csv'), "w", newline='') as file_output:
            csv_output = csv.DictWriter(file_output, fieldnames=headings)
            csv_output.writeheader()

            for key, item in self.entities.items():
                row = {"Entity": key, "Concept": "\n".join(item["Concept"]),
                       "Description": item["Entity Description"] if item["Entity Description"] else item[
                           "Concept Description"], "Source": item["Source"]}
                csv_output.writerow(row)
    def convert_data_structures(self):
        headings = ["Structure", "Description", "Source"]

        with open(os.path.join(os.path.dirname(__file__), 'csv_output', 'Data_Structures.csv'), "w", newline='') as file_output:
            csv_output = csv.DictWriter(file_output, fieldnames=headings)
            csv_output.writeheader()

            for key, item in self.structures.items():
                row = {"Structure": key, "Description": item["Description"], "Source": item["Source"]}


if __name__ == '__main__':
    csvConvert(
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Logical Model.csv'),
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Concept Model.csv'),
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Data Structures.csv'),
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Terminology.csv'),
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Use Cases.csv'))
