DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS recipes;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  fullname TEXT DEFAULT '',
  gender TEXT,
  weight REAL,
  height REAL,
  restrictions TEXT DEFAULT '',
  is_config INTEGER NOT NULL DEFAULT 0,
  liked TEXT
);
