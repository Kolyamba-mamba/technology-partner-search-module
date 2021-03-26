class Patent:
    """Класс патента"""

    def __init__(self, publication_reference, main_classification_type, main_classification,
                 title, inventors, abstract_path, description_path, claims_path):
        self.publication_reference = publication_reference
        self.main_classification_type = main_classification_type
        self.main_classification = main_classification
        self.title = title
        self.inventors = inventors
        self.abstract_path = abstract_path
        self.description_path = description_path
        self.claims_path = claims_path
