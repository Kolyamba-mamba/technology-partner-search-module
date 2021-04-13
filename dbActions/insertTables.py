from models.patent import Patent
from models.sao import Sao
from helpers.dbHelper import execute_query_with_params


def insert_patent(connection, patent: Patent):
    insert_query = """
    INSERT INTO patents (
    id, 
    publication_reference, 
    main_classification_type, 
    main_classification, 
    title, 
    inventors, 
    abstract_path, 
    description_path, 
    claims_path)
    values 
    (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    execute_query_with_params(connection, insert_query, list(patent.__dict__.values()))


def insert_sao(connection, sao: Sao):
    pass