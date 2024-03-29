class ParsedPatent:
    """Класс патентных данных после парсинга"""

    def __init__(self, application_reference, publication_reference, main_classification_type, main_classification,
                 title, inventors, abstract, description, claims, assignee):
        self.application_reference = application_reference
        self.publication_reference = publication_reference
        self.main_classification_type = main_classification_type
        self.main_classification = main_classification
        self.title = title
        self.inventors = inventors
        self.abstract = abstract
        self.description = description
        self.claims = claims
        self.assignee = assignee