import os
import graphviz
import csv


class EntityModels:
    def __init__(self, filepath_logical_model, filepath_concept_model, filepath_data_structures, filepath_terminology):
        self.FilePathLogicalModel = filepath_logical_model
        self.FileConceptModel = filepath_concept_model
        self.FileDataStructure = filepath_data_structures
        self.FileTerminology = filepath_terminology
        self.port_id = 0
        self.concepts = self.generate_concepts()
        self.conceptsOf = self.generate_concepts_of()
        self.entities = self.generate_entities()
        self.structures = self.generate_data_structures()
        # self.terminology = self.generate_terminology()
        self.generate_dot_code("png")
        self.generate_dot_code("svg")

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
                                                "Label": row["Label"] if row["Label"] else strip_savvi(row["Concept"]),
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
                        concepts[previous_row["Concept"]]["Relationship"].append({"Relationship": row["Relationship"],
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
                        concepts_of[row["Object"]].append({"Object": row["Object"], "Relationship": row["Relationship"],
                                                           "Concept": row["Concept"], "Label": row["Label"]})
                else:
                    if row["Object"]:
                        concepts_of[row["Object"]].append({"Object": row["Object"], "Relationship": row["Relationship"],
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

                    entities[row["Entity"]] = {"Entity": row["Entity"], "Concept": row["Concept"],
                                               "Concept Description": row["Concept Description"],
                                               "Entity Description": row["Entity Description"], "Attributes": []}

                    if row["Attributes"]:
                        entities[row["Entity"]]["Attributes"].append(
                            {"Attributes": row["Attributes"], "Description": row["Description"],
                             "Field Type": row["Field Type"], "Data Structure": row["Data Structure"],
                             "Occurs": row["Occurs"], "Required": row["Required"],
                             "Permitted Values": row["Permitted Values"]})
                else:
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

    def generate_dot_code(self, file_format):
        for key, item in self.entities.items():
            dot = setup_digraph()

            table = f"<<table border='0' cellborder='1' cellspacing='0'><tr><td colspan='3' bgcolor='lightblue'> " \
                    f"{item['Entity']}</td></tr>" \
                    f"<tr><td bgcolor='lightblue'>Attribute</td>" \
                    f"<td bgcolor='lightblue'>Field</td>" \
                    f"<td bgcolor='lightblue'>Occurs</td></tr>"
            if len(item["Attributes"]):
                for attr in item["Attributes"]:
                    if attr["Data Structure"] != '':
                        port = self.create_structure_port(dot, attr["Data Structure"], item["Entity"])
                    else:
                        port = ""
                    table += f"<tr><td align='left' balign='left' valign='top'>{attr['Attributes']}</td>" \
                             f"<td align='left' balign='left' valign='top'>{attr['Field Type'] if attr['Field Type'] else attr['Data Structure']}</td>" \
                             f"<td align='left' balign='left' valign='top'{port}>{attr['Occurs']}</td></tr>"
            table += "</table>>"
            dot.node(item["Entity"], table, _attributes={"shape": "plaintext", "URL": f"#{item['Entity']}"})
            if item["Concept"] != '':
                for con in self.concepts[item["Concept"]]["Relationship"]:
                    dot.node(f'Concept_{self.concepts[con["Object"]]["Label"]}', self.concepts[con["Object"]]["Label"],
                             _attributes={"height": "0.8", "width": "1.0", "style": "filled", "fixedsize": "true",
                                          "URL": f'#{strip_savvi(item["Concept"])}'})
                    dot.edge(item["Entity"], f'Concept_{self.concepts[con["Object"]]["Label"]}', con["Relationship"])

            if item["Concept"] != '' and len(self.conceptsOf[item["Concept"]]):
                for con in self.conceptsOf[item["Concept"]]:
                    dot.node(f'ConceptOf_{con["Label"]}', con["Label"],
                             _attributes={"height": "0.8", "width": "1.0", "style": "filled", "fixedsize": "true",
                                          "URL": f'#{strip_savvi(item["Concept"])}'})
                    dot.edge(f'ConceptOf_{con["Label"]}', item["Entity"], con["Relationship"])

            print(dot.source)
            dot.format = "svg"
            dot.render(os.path.join(os.path.dirname(__file__), f'graph_output/entity/{item["Entity"]}.gv'), view=False)
            dot.format = "png"
            dot.render(os.path.join(os.path.dirname(__file__), f'graph_output/entity/{item["Entity"]}.gv'), view=False)

    def create_structure_port(self, dot, structure, node_id):
        self.port_id += 1

        table = f"<<table border='0' cellborder='1' cellspacing='0'>" \
                f"<tr><td bgcolor='lightblue'>Attribute</td>" \
                f"<td bgcolor='lightblue'>Type</td>" \
                f"<td bgcolor='lightblue'>Occurs</td></tr>"

        for row in self.structures[structure]:
            table += f"<tr><td align='left' balign='left' valign='top'>{row['Attribute']}</td>" \
                     f"<td align='left' balign='left' valign='top'>{row['Type']}</td>" \
                     f"<td align='left' balign='left' valign='top'>{row['Occurs']}</td></tr>"
        table += "</table>>"
        dot.node(f"table_port{self.port_id}", table, _attributes={"shape": "plaintext"})
        dot.edge(f"{node_id}:{self.port_id}", f"table_port{self.port_id}", _attributes={"dir": "none"})
        return f" port='{self.port_id}'"


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
    EntityModels(os.path.join(os.path.dirname(__file__), 'csv/SAVVI Concept and Logical Model - Logical Model.csv'),
                 os.path.join(os.path.dirname(__file__), 'csv/SAVVI Concept and Logical Model - Concept Model.csv'),
                 os.path.join(os.path.dirname(__file__), 'csv/SAVVI Concept and Logical Model - Data Structures.csv'),
                 os.path.join(os.path.dirname(__file__), 'csv/SAVVI Concept and Logical Model - Terminology.csv'))
