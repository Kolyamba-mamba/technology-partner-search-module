from helpers.dbHelper import execute_select_all_query, get_cursor_query


def get_count_table_rows(connection, table_name):
    query = f"SELECT COUNT(*) FROM {table_name}"
    count = execute_select_all_query(connection, query)
    return count


def get_entities(connection, table_name):
    query = f"SELECT * FROM {table_name} ORDER BY id"
    ids = execute_select_all_query(connection, query)
    return ids


def get_cursor(connection, table_name):
    query = f"SELECT * FROM {table_name}"
    cursor = get_cursor_query(connection, query)
    return cursor