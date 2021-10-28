import datetime
import sqlite3


# from database import create_connection


def create_table(conn):
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE results
                    (ID INT PRIMARY KEY       NOT NULL,
                    PATH        TEXT     NOT NULL,
                    NAME        TEXT     NOT NULL,
                    SIZE             TEXT     NOT NULL,
                    rules        TEXT     NOT NULL,
                    search       INTEGER  NOT NULL,
                    FOREIGN KEY(search) REFERENCES search_query(ID)
                    );''')
        conn.commit()
    except sqlite3.OperationalError as e:
        print(e)


def insert_result(conn, result):
    sql = ''' INSERT INTO results(ID,PATH,NAME,SIZE,rules,search)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, result)
    conn.commit()

    return cur.lastrowid


def select_all_results(conn):
    sql = '''SELECT * FROM results'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

    return cur.fetchall()
