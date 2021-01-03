import os
import graphviz
import csv


class ConceptModel:
    """
    Generating a Graphviz diagram for the Concept Model
    """

    def __init__(self, file_concept_model: str):
        """
        :param file_concept_model: Filepath to Concept Model CSV
        """
        self.fileConceptModel = file_concept_model
        self.concepts = self.generate_concepts()
        dot = self.generate_dot_code()
        dot = self.generate_dot_code()

        print(dot.source)
        dot.format = "svg"
        dot.render(os.path.join(os.path.dirname(__file__), 'graph_output/conceptModel.gv'), view=False)
        dot.format = "png"
        dot.render(os.path.join(os.path.dirname(__file__), 'graph_output/conceptModel.gv'), view=False)

    def generate_concepts(self) -> dict:
        """
        Converts the CSV into a dict while added multiple relationships to a single concept
        """
        with open(self.fileConceptModel, "r", errors="REPLACE") as file_concept_model:
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

    def generate_dot_code(self):
        dot = graphviz.Digraph()
        dot.node_attr = {"color": "black", "fillcolor": "lightblue", "fontname": "Arial", "black": "black",
                         "fontsize": "7"}
        dot.edge_attr = {"fontname": "Arial", "fontsize": "7", "labelfontname": "Arial", "labelfontsize": "7",
                         "len": "3.0"}
        dot.graph_attr = {"overlap": "false", "splines": "true"}

        for (key, item) in self.concepts.items():
            dot.node(strip_savvi(key), item["Label"],
                     _attributes={"height": "0.8", "width": "1.0", "style": "filled", "fixedsize": "true",
                                  "URL": f'#{strip_savvi(item["Concept"])}'})
        for (key, item) in self.concepts.items():
            if len(item["Relationship"]):
                for rel in item["Relationship"]:
                    dot.edge(strip_savvi(key), strip_savvi(rel["Object"]), rel["Relationship"])

        return dot


def strip_savvi(text):
    return text.split(":")[1]


if __name__ == '__main__':
    ConceptModel(os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Concept Model.csv'))
