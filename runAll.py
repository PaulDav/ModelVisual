import os

from conceptModel import ConceptModel
from entityModels import EntityModels
from entireEntityModel import EntireEntityModel
from useCases import UseCaseModels
from csvConvert import CsvConvert

FileLogicalModel = str(
    os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Logical Model.csv'))
FileConceptModel = str(
    os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Concept Model.csv'))
FileDataStructures = str(os.path.join(os.path.dirname(__file__), 'csv',
                                      'SAVVI Concept and Logical Model - Data Structures.csv'))
FileTerminology = str(
    os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Terminology.csv'))
FileUseCases = str(os.path.join(os.path.dirname(__file__), 'csv', 'SAVVI Concept and Logical Model - Use Cases.csv'))

ConceptModel(FileConceptModel)
EntityModels(FileLogicalModel, FileConceptModel, FileDataStructures, FileTerminology)
EntireEntityModel(FileLogicalModel, FileConceptModel, FileDataStructures, FileTerminology)
UseCaseModels(FileLogicalModel, FileConceptModel, FileDataStructures, FileTerminology, FileUseCases)
CsvConvert(FileLogicalModel, FileConceptModel, FileDataStructures, FileTerminology, FileUseCases)
