import json
import os
import psycopg2 as ps



def read_config(path:str = "config.json"):
    """
    Reads the configuration from a JSON file and returns it as a dictionary.
    :param path:The path to the configuration file (default is "config.json").
    :return:A dictionary containing the configuration data from the JSON file.
    """
    with open(path, "r") as f:
        conf = json.loads(f.read())
    return conf

config = read_config()
database_config = config['database_config']
database_config['password'] = os.environ['postgres']

def read_from_db(query: str,db_conf: dict = database_config, params = ()) -> list:
    """
    Executes a read query on the database and returns the results as a list of dictionaries.
    :param query: The SQL query to execute
    :param db_conf:The database configuration
    :param params:Optional parameters to pass to the query to prevent SQL injection
    :return:A list of dictionaries, where each dictionary represents a row of data with column names as keys.
    """
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
    """
    Fetches the borrowing history of a user, including the book title, author, genre, loan date, and return date.
    :param user_id:int - User's unique identifier.
    :param db_conf: dict - Database connection configuration (default: `database_config`).
    :return:List of books with details (title, author, genre, loan date, return date).
    """
    try:
        with ps.connect(**db_conf) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                           select distinct on (b.book_id) b.title, a.full_name as author,g.genre_name as genre,l.loan_date,l.return_date
                           from project.loans l
                           join project.books b on l.book_id = b.book_id
                           join project.authors a on b.author_id = a.author_id
                           join project.genres g on b.genre_id = g.genre_id
                           where l.user_id = %s
                           order by b.book_id, l.return_date DESC
                       """, (user_id,))
                response = cursor.fetchall()
                return response
    except Exception as e:
        print(f"Failed to get data {e}")
        return [f"error: message {e}"]

def write_to_db(query: str, db_conf: dict = database_config, params=()) -> None:
    """
     Executes a write query to the database.
    :param query:The SQL query to be executed.
    :param db_conf:The database configuration details (default is `database_config`).
    :param params:Optional parameters for the query to prevent SQL injection
    :return: The function performs a write operation and commits the changes to the database.
    """
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
    print(read_from_db(f"select username, password from project.users where username = 'admin2'"))
    print(read_from_db("select * from project.authors where full_name = 'John Doe'"))
    print(read_from_db("select full_name from project.authors"))
