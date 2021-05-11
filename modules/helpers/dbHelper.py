import psycopg2


def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Подключение к PostgreSQL установлено")
    except psycopg2.OperationalError as e:
        print(f"Ошибка '{e}' при подключении к БД")
    return connection


def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # print("Запрос прошел успешно")
    except psycopg2.OperationalError as e:
        print(f"Ошибка '{e}' при выполнении запроса")


def execute_query_with_params(connection, query, params):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        # print("Запрос прошел успешно")
    except psycopg2.OperationalError as e:
        print(f"Ошибка '{e}' при выполнении запроса")


def execute_select_all_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # print("Запрос прошел успешно")
        return cursor.fetchall()
    except psycopg2.OperationalError as e:
        print(f"Ошибка '{e}' при выполнении запроса")


def get_cursor_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # print("Запрос прошел успешно")
        return cursor
    except psycopg2.OperationalError as e:
        print(f"Ошибка '{e}' при выполнении запроса")


def create_tables(connection):
    create_patents_table = """
    CREATE TABLE IF NOT EXISTS patents (
    id uuid NOT NULL PRIMARY KEY,
    publication_reference TEXT NOT NULL,
    main_classification_type TEXT NOT NULL,
    main_classification TEXT,
    title TEXT,
    inventors TEXT,
    abstract_path TEXT,
    description_path TEXT,
    claims_path TEXT,
    assignee TEXT
    )
    """

    create_sao_table = """
        CREATE TABLE IF NOT EXISTS sao (
        id uuid NOT NULL PRIMARY KEY,
        subject TEXT,
        action TEXT,
        object TEXT,
        patent_id uuid NOT NULL
        )
        """

    execute_query(connection, create_patents_table)
    execute_query(connection, create_sao_table)
