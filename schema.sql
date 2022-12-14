DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

CREATE TABLE users (
  user TEXT PRIMARY KEY,
  mail TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  isbn TEXT NOT NULL,
  content TEXT NOT NULL,
  FOREIGN KEY (username) REFERENCES users (user),
  FOREIGN KEY (isbn) REFERENCES books (isbn)
);

CREATE TABLE books (
  isbn TEXT PRIMARY KEY,
  book TEXT NOT NULL,
  author TEXT NOT NULL,
  genre TEXT NOT NULL,
  imagelink TEXT NOT NULL,
  amazonlink TEXT NOT NULL
);

CREATE TABLE ratings (
  isbn TEXT NOT NULL,
  user TEXT NOT NULL,
  rating INTEGER NOT NULL,
  PRIMARY KEY (user, isbn),
  FOREIGN KEY (user) REFERENCES users (user),
  FOREIGN KEY (isbn) REFERENCES books (isbn)
);
