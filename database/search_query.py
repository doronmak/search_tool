import datetime
import sqlite3


# from database import create_connection


def create_table(conn):
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE search_query
                 (ID INT PRIMARY KEY      NOT NULL,
                 FOLDER_PATH     TEXT     NOT NULL,
                 NAMES           TEXT     NOT NULL,
                 SIZES           TEXT     NOT NULL,
                 EXTENSIONS      TEXT     NOT NULL,
                 DATE            TEXT     NOT NULL);''')
        conn.commit()
    except sqlite3.OperationalError as e:
        print(e)


def insert_search_query(conn, search_query):
    sql = ''' INSERT INTO search_query(ID,FOLDER_PATH,NAMES,SIZES,EXTENSIONS,DATE)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, search_query)
    conn.commit()

    return cur.lastrowid


def select_search_query(conn):
    sql = '''SELECT * FROM search_query'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

    return cur.fetchall()
