CREATE TABLE IF NOT EXISTS authors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    webhook TEXT DEFAULT NULL,
    api_key TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS posts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    FOREIGN KEY (author_id) REFERENCES authors(id) 
                                );

CREATE TABLE IF NOT EXISTS comments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    parent_id INTEGER DEFAULT NULL,
    author_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    content TEXT NOT NULL,

    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (parent_id) REFERENCES comments(id),
    FOREIGN KEY (author_id) REFERENCES authors(id)
                                );
