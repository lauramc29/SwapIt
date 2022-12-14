import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import json 
import re
import pandas as pd
import math

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

### REGISTRATION - INSERT VALUES
def register_user_to_db(user, password, mail):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO users(user,password,mail) values (?,?,?)', (user, password, mail))
    conn.commit()
    conn.close()

def register_post_to_db(username, isbn, book, content):
    conn = get_db_connection()
    conn.execute('INSERT INTO posts(username,isbn,title,content) values (?,?,?,?)', (username, isbn, book, content))
    conn.commit()
    conn.close()

def register_rating_to_db(username, isbn, rating):
    conn = get_db_connection()
    conn.execute('INSERT INTO ratings(user,isbn,rating) values (?,?,?)', (username, isbn, rating))
    conn.commit()
    conn.close()

### CHECK IF USER EXISTS IN DATABASE
def check_user(username, password):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT user,password FROM users WHERE user=? and password=?', (username, password))
    result = cur.fetchone()
    
    if result:
        return True
    else:
        return False
    
def valid_register(username, mail):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    res_mail = cur.execute('SELECT mail FROM users WHERE mail=?', (mail,)).fetchone()
    res_user = cur.execute('SELECT user FROM users WHERE user=?', (username,)).fetchone()
    
    if res_mail or res_user:
        return False
    else:
        return True

def valid_post(content):
    url = "https://api.apilayer.com/bad_words?censor_character=*"
       
    if not content:
        return 2
    
    cleanString = re.sub('\W+',' ', content).encode("utf-8")

    headers= {
        "apikey": "ezdJ8Qt7qVLADpnpaieeAeGaLw7itA8I"
    }

    response = requests.request("POST", url, headers=headers, data = cleanString)
    status_code = response.status_code
    result = response.text
    resultjs = json.loads(result)

    num_insults = int(resultjs['bad_words_total'])
    
    if num_insults > 0:
        return False
               
    return True
  
app = Flask(__name__)
app.secret_key = "r@nd0mSk_1"

@app.route('/', methods=['GET'])
def intro():
    if session.get("username"):
        return redirect(url_for('books'))
    else:
        return render_template('intro.html')
      
@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get("username"):
        return redirect(url_for('books'))
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            session['username'] = username
            return redirect(url_for('books'))
        else:
            error = 'Invalid username/password'

    return render_template('login.html', error=error)

@app.route('/register', methods=["POST", "GET"])
def register():
    if session.get("username"):
        return redirect(url_for('books'))
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        mail = request.form['mail']
        if valid_register(username, mail):
            register_user_to_db(username, password, mail)
            return redirect(url_for('login'))
        else:
            error = 'Username or Email already used'

    return render_template('register.html', error=error)
    
@app.route('/posts', methods=['POST', 'GET'])
def posts():
    if not session.get("username"):
        return redirect(url_for('login'))
    error = None
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created DESC').fetchall()
    conn.close()
    return render_template('posts.html', posts=posts, error=error)

@app.route('/books', methods=['POST', 'GET'])
def books():
    if not session.get("username"):
        return redirect(url_for('login'))
    error = None
    conn = get_db_connection()
    username = session.get("username")
    
    ### books from user session
    books = conn.execute('SELECT book,imagelink,amazonlink FROM books INNER JOIN ratings ON books.isbn = ratings.isbn WHERE ratings.user=?', (username,)).fetchall()
    books_users = conn.execute('SELECT isbn,rating,user FROM ratings').fetchall()
    tops = conn.execute('SELECT book,imagelink,amazonlink,AVG(ratings.rating) AS rating FROM books INNER JOIN ratings ON books.isbn = ratings.isbn GROUP BY book ORDER BY ratings.rating DESC LIMIT 5').fetchall()
    
    recommendations = recommend(books_users)
    
    conn.close()
    return render_template('books.html', books=books, tops=tops, recommendations=recommendations, error=error)
        
def recommend(books_users):
    username = session.get("username")
    
    books_users = pd.DataFrame(books_users,columns=["isbn","rating","user"])
    book_user = books_users[books_users['user'] == username]
    
    userSubset = books_users[books_users['isbn'].isin(book_user['isbn'].tolist())]
    userSubsetGroup = userSubset.groupby(['user'])
    userSubsetGroup = sorted(userSubsetGroup, key=lambda x: len(x[1]), reverse=True)
    userSubsetGroup = userSubsetGroup[1:100]

    llista_posibles_llibres = pd.DataFrame(columns=['user', 'isbn'])

    if len(userSubsetGroup)!=0:

        
        pearsonCorrelationDict = {}
        #Para cada grupo de usuarios de nuestro subconjunto 
        for ID, other in userSubsetGroup:
            
            othersBooks= other.sort_values(by='isbn')
            usuariBooks= book_user.sort_values(by='isbn')

            temp_df = usuariBooks[usuariBooks['isbn'].isin(othersBooks['isbn'].tolist())]

            tempRatingList = temp_df['rating'].tolist()

            tempGroupList = othersBooks['rating'].tolist()

            data_corr = {'tempGroupList': tempGroupList,'tempRatingList': tempRatingList}
            
            pd_corr = pd.DataFrame(data_corr)
            
            r = pd_corr.corr(method="pearson")["tempRatingList"]["tempGroupList"]
            
        
            if math.isnan(r) == True:
                r = 0
            pearsonCorrelationDict[ID] = r
            
            
        #Convertimos el diccionario a un dataframe:         
        pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
        pearsonDF.columns = ['Correlació']
        pearsonDF['user'] = pearsonDF.index
        pearsonDF.index = range(len(pearsonDF))
        pearsonDF.head()
        
        pearsonDF = pearsonDF[pearsonDF['Correlació']>0]
        if len(pearsonDF)>5:
            pearsonDF = pearsonDF[0:5]
            
        long = len(pearsonDF)
        
        
        if long!=0:
            operacio= 5//long
        
            for book in pearsonDF['user']:
                
                USER_OTHER = books_users[books_users['user']==book]
                
                # els llibres que no tenen en comú:
                USER_OTHER = USER_OTHER[~USER_OTHER['isbn'].isin(book_user['isbn'].tolist())]
                USER_OTHER = USER_OTHER[~USER_OTHER['isbn'].isin(llista_posibles_llibres['isbn'])]
                USER_OTHER = USER_OTHER.sort_values(by='rating')
                nou_llibre = USER_OTHER[['isbn', 'user']][0:operacio]
                llista_posibles_llibres = pd.concat([llista_posibles_llibres, nou_llibre])
                
        else:
                
            groupByBooks = books_users.groupby('isbn',as_index=False)['rating'].mean()
            groupByBooks = groupByBooks.sort_values(by='rating', ascending= False)
            llista_posibles_llibres = groupByBooks[0:5]
            
    else:
                
            groupByBooks = books_users.groupby('isbn',as_index=False)['rating'].mean()
            groupByBooks = groupByBooks.sort_values(by='rating', ascending= False)
            llista_posibles_llibres = groupByBooks[0:5]
            
    isbn_possibles_llibres = tuple(llista_posibles_llibres['isbn'])
    long = len(isbn_possibles_llibres)
    
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM books WHERE isbn IN ({})'.format(', '.join(['?'] * long)), [*isbn_possibles_llibres,]).fetchall()
    conn.close()
    return posts

@app.route('/create', methods=('GET', 'POST'))
def create():
    if not session.get("username"):
        return redirect(url_for('login'))
    
    error = None
    
    conn = get_db_connection()
    nom_books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    
    if request.method == 'POST':
        username = session.get("username")
        isbn = request.form['isbn']  
        content = request.form['content']
        
        out = valid_post(content)
        
        if out == True:
            conn = get_db_connection()
            books1 = conn.execute('SELECT * FROM ratings WHERE user=? AND isbn=?', (username,isbn)).fetchall()
            books2 = conn.execute('SELECT * FROM books WHERE isbn=?', (isbn,)).fetchall()
            
            conn.close()
            
            if request.form['rating']:
                rating = request.form['rating'] 
                if len(books1)>0:
                    return render_template('create.html', error="You have already read this book", data=nom_books)
                else:
                    register_rating_to_db(username, isbn, rating) ############### isbn COGER

            register_post_to_db(username, isbn, books2[0]['book'], content)
            return redirect(url_for('posts'))
        
        elif out == 2:
            error = 'The content is missing'
            
        else: 
            error = 'Cannot be posted, it contains offensive words'
            
    return render_template('create.html', error=error, data=nom_books)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()