#TODO Add a table for authors and use author ID to referee to them
#TODO Upload an empty version of the db then add it to the .gitignore (Sorry for that)
from datetime import datetime
from pathlib import Path

HOME = Path(__file__).resolve().parent

def create(connection):
    with open(HOME / "schema.sql","r") as f:
         script = f.read()
    connection.executescript(script)

def dropAllTables(connection):
     connection.execute("DROP TABLE authors")
     connection.execute("DROP TABLE posts")
     connection.execute("DROP TABLE comments")
    
#POST Related 
def displayPosts(connection):
     return connection.execute("SELECT id,author,date,title FROM posts")

def getPost(connection,post_id):
     return connection.execute("SELECT * FROM posts WHERE id = ?",[post_id])

def getAuthor(connection,post_id):
     return connection.execute("SELECT author FROM posts WHERE id = ?",[post_id])

def getRandomPost(connection,author=None):
     if(author): return connection.execute("SELECT id,content FROM posts p WHERE author != ? AND NOT EXISTS(SELECT 1 FROM comments c WHERE c.author = ? and c.post_id == p.id) ORDER BY RANDOM() LIMIT 1",[author,author])
     return connection.execute("SELECT id,content FROM posts ORDER BY RANDOM() LIMIT 1")

def addPost(connection,author,title,content):
     time = datetime.strftime(datetime.now(),"%d %b %Y-%H:%M")
     connection.execute("INSERT INTO posts (author,date,title,content) VALUES (?,?,?,?);",[author,time,title,content])
     connection.commit()

#Comment related
def addComment(connection,author,content,postID,parentID=None):
     time = datetime.strftime(datetime.now(),"%d %b %Y-%H:%M")
     cursor = connection.execute("INSERT INTO comments (author,date,content,post_id,parent_id) VALUES (?,?,?,?,?) RETURNING id;",[author,time,content,postID,parentID])
     result = cursor.fetchone()
     connection.commit()
     return result

def getComments(connection,postID):
     return connection.execute("SELECT c.*,r.content as ReplayContent FROM comments c LEFT JOIN comments r ON r.parent_id = c.ID WHERE c.post_id = ? AND c.parent_id IS NULL",[postID])


