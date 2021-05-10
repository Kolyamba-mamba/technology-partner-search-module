import os
import sys
sys.path.append(os.path.abspath('../../mySite/mySite'))
from modules.models.patent import Patent
from modules.models.sao import Sao
from modules.helpers.dbHelper import execute_query_with_params


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
    insert_query = """
        INSERT INTO sao (
        id, 
        subject,
        action, 
        object,
        patent_id)
        values 
        (%s,%s,%s,%s,%s)
        """
    execute_query_with_params(connection, insert_query, list(sao.__dict__.values()))