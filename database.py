import sqlite3

def create_connection(db_file):
    """ crea una connessione al database SQLite specificato dal db_file """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ crea una tabella dal create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def initialize_db():
    database = r"cache.db"

    sql_create_cache_table = """ CREATE TABLE IF NOT EXISTS api_cache (
                                    url TEXT PRIMARY KEY,
                                    response TEXT,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                                ); """

    # crea una connessione al database
    conn = create_connection(database)

    # crea tabelle
    if conn is not None:
        # crea tabella cache
        create_table(conn, sql_create_cache_table)
    else:
        print("Errore! Impossibile creare la connessione al database.")

if __name__ == '__main__':
    initialize_db()
