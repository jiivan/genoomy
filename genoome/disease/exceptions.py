class DiseaseError(Exception):
    "Base class for disease module exceptions."
    pass

class ParserError(DiseaseError): pass
