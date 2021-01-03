import os
import graphviz
import csv


class EntireEntityModel:
    def __init__(self, filepath_logical_model, filepath_concept_model, filepath_data_structures, filepath_terminology):
        self.FilePathLogicalModel = filepath_logical_model
        self.FileConceptModel = filepath_concept_model
        self.FileDataStructure = filepath_data_structures
        self.FileTerminology = filepath_terminology
        self.port_id = 0
        self.concepts = self.generate_concepts()
        self.conceptsOf = self.generate_concepts_of()
        self.conceptOfEntity = {}
        self.entities = self.generate_entities()
        self.structures = self.generate_data_structures()
        # self.terminology = self.generate_terminology()
        self.generate_dot_code()

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
                                               "Entity Description": row["Entity Description"], "Attributes": []}

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

    def generate_dot_code(self):
        dot = setup_digraph()
        entities = []
        for key, item in self.entities.items():
            table = f"<<table border='0' cellborder='1' cellspacing='0'><tr><td colspan='3' bgcolor='lightblue'> " \
                    f"{item['Entity']}</td></tr>" \
                    f"<tr><td bgcolor='lightblue'>Attribute</td>" \
                    f"<td bgcolor='lightblue'>Field</td>" \
                    f"<td bgcolor='lightblue'>Occurs</td></tr>"
            if len(item["Attributes"]):
                for attr in item["Attributes"]:
                    table += f"<tr><td align='left' balign='left' valign='top'>{attr['Attributes']}</td>" \
                             f"<td align='left' balign='left' valign='top'>" \
                             f"{attr['Field Type'] if attr['Field Type'] else attr['Data Structure']}</td>" \
                             f"<td align='left' balign='left' valign='top'>{attr['Occurs']}</td></tr>"
            table += "</table>>"

            dot.node(item["Entity"], table, _attributes={"shape": "plaintext", "URL": f"#{item['Entity']}"})
            entities.append(item["Entity"])
        nodeConcept = []
        for entity in entities:
            for concept in self.entities[entity]["Concept"]:
                if self.concepts.get(concept, False) and self.concepts[concept]["Relationship"]:
                    for rel in self.concepts[concept]["Relationship"]:
                        if rel["Object"] in self.conceptOfEntity:
                            dot.edge(entity, self.conceptOfEntity[rel["Object"]], rel["Relationship"])
                        else:
                            if rel["Object"] in nodeConcept:
                                dot.edge(entity, f'node{strip_savvi(rel["Object"])}', rel["Relationship"])
                            else:
                                dot.node(f'node{strip_savvi(rel["Object"])}', self.concepts[rel["Object"]]["Label"],
                                         _attributes={"height": "0.8", "width": "1.0", "style": "filled",
                                                      "fixedsize": "true",
                                                      "URL": f'#{strip_savvi(rel["Object"])}'})
                                dot.edge(entity, f'node{strip_savvi(rel["Object"])}', rel["Relationship"])

                                for con in self.concepts[rel["Object"]]["Relationship"]:
                                    dot.edge(f'node{strip_savvi(rel["Object"])}',
                                             self.conceptOfEntity[con["Object"]],
                                             con["Relationship"])

                                nodeConcept.append(rel["Object"])

        print(dot.source)
        dot.format = "png"
        dot.render(os.path.join(os.path.dirname(__file__), f'graph_output/EntireEntityModel.gv'), view=False)
        dot.format = "svg"
        dot.render(os.path.join(os.path.dirname(__file__), f'graph_output/EntireEntityModel.gv'), view=False)


def setup_digraph():
    dot = graphviz.Digraph()
    dot.node_attr = {"color": "black", "fillcolor": "lightblue", "fontname": "Arial", "black": "black",
                     "fontsize": "7"}
    dot.edge_attr = {"fontname": "Arial", "fontsize": "7", "labelfontname": "Arial", "labelfontsize": "7",
                     "len": "3.0"}
    dot.graph_attr = {"overlap": "false", "splines": "true"}

    return dot


def strip_savvi(text):
    return text.split(":")[1]


if __name__ == '__main__':
    EntireEntityModel(
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Logical Model.csv'),
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Concept Model.csv'),
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Data Structures.csv'),
        os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Terminology.csv'))
