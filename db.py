import pandas as pd
import sqlite3

users = pd.read_excel(
    'data/users.xlsx',
    header = 0)

posts = pd.read_excel(
    'data/posts.xlsx',
    header = 0)

books = pd.read_excel(
    'data/books.xlsx',
    header = 0)

ratings = pd.read_excel(
    'data/ratings.xlsx',
    header = 0)

def init_db(users, posts):
    db_conn = sqlite3.connect("database.db")
    c = db_conn.cursor()
    with open('schema.sql') as f:
        c.executescript(f.read())
        
    users.to_sql('users', db_conn, if_exists='append', index=False)
    posts.to_sql('posts', db_conn, if_exists='append', index=False)
    books.to_sql('books', db_conn, if_exists='append', index=False)
    ratings.to_sql('ratings', db_conn, if_exists='append', index=False)
    
    db_conn.commit()
    
    print("USERS")
    print(pd.read_sql("SELECT * FROM users", db_conn))
    
    print("BOOKS")
    print(pd.read_sql("SELECT * FROM books", db_conn))
    
    print("RATINGS")
    print(pd.read_sql("SELECT * FROM ratings", db_conn))
        
    db_conn.close()

init_db(users, posts)


# Create a SQL connection to our SQLite database
# db_conn = sqlite3.connect("database.db")
# df = pd.read_sql_query('SELECT * FROM posts', db_conn)
# print(df)
# db_conn.close()

