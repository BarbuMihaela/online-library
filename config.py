import json
import os

import psycopg2 as ps



def read_config(path:str = "config.json"):
    with open(path, "r") as f:
        conf = json.loads(f.read())
    return conf

config = read_config()
database_config = config['database_config']
database_config['password'] = os.environ['postgres']

def read_from_db(query: str,db_conf: dict = database_config, params = ()) -> list:
    try:
        with ps.connect(**db_conf) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                response = cursor.fetchall()
                columns = [item.name for item in cursor.description]
                new_data = []
                for item in response:
                    new_data.append(dict(zip(columns, item)))
                return new_data
    except Exception as e:
        print(f"Failed to get data {e}")
        return [f"error: message {e}"]

def all_books_history(user_id: int, db_conf: dict = database_config) -> list:
    try:
        with ps.connect(**db_conf) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                           select b.title, a.full_name as author,g.genre_name as genre,l.loan_date,l.return_date
                           from project.loans l
                           join project.books b on l.book_id = b.book_id
                           join project.authors a on b.author_id = a.author_id
                           join project.genres g on b.genre_id = g.genre_id
                           where l.user_id = %s
                           order by l.return_date DESC
                       """, (user_id,))
                response = cursor.fetchall()
                return response
    except Exception as e:
        print(f"Failed to get data {e}")
        return [f"error: message {e}"]

def write_to_db(query: str, db_conf: dict = database_config, params=()) -> None:
    try:
        with ps.connect(**db_conf) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
    except Exception as e:
        print(f"Failed to write data: {e}")



if __name__ == '__main__':
    config = read_config()
    database_config = config['database_config']
    database_config['password'] = os.environ['postgres']
    # print(read_from_db("select * from project.users;", database_config))
    print(read_from_db(f"select username, password from project.users where username = 'admin2'"))
    print(read_from_db("select * from project.authors where full_name = 'John Doe'"))
    print(read_from_db("select full_name from project.authors"))
