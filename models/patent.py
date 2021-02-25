class Patent:
    """Класс патента"""

    def __init__(self, application_reference, publication_reference, main_classification_type, main_classification,
                 abstract, description, claims):
        self.application_reference = application_reference
        self.publication_reference = publication_reference
        self.main_classification_type = main_classification_type
        self.main_classification = main_classification
        self.abstract = abstract
        self.description = description
        self.claims = claims
