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
    # connection.execute("DROP TABLE POSTS")
     connection.execute("DROP TABLE COMMENTS")
    
#POST Related 
def displayPosts(connection):
     return connection.execute("SELECT ID,Author,Date,Title FROM POSTS")

def getPost(connection,post_id):
     return connection.execute("SELECT * FROM POSTS WHERE ID = ?",[post_id])

def getRandomPost(connection,author=None):
     if(author): return connection.execute("SELECT ID,Content FROM POSTS p WHERE Author != ? AND NOT EXISTS(SELECT 1 FROM COMMENTS c WHERE c.Author = ? and c.PostID == p.ID) ORDER BY RANDOM() LIMIT 1",[author,author])
     return connection.execute("SELECT ID,Content FROM POSTS ORDER BY RANDOM() LIMIT 1")

def addPost(connection,author,title,content):
     time = datetime.strftime(datetime.now(),"%d %b %Y-%H:%M")
     connection.execute("INSERT INTO POSTS (Author,Date,Title,Content) VALUES (?,?,?,?);",[author,time,title,content])
     connection.commit()

#Comment related
def addComment(connection,author,content,postID,parentID=None):
     time = datetime.strftime(datetime.now(),"%d %b %Y-%H:%M")
     cursor = connection.execute("INSERT INTO COMMENTS (Author,Date,Content,PostID,ParentID) VALUES (?,?,?,?,?) RETURNING ID;",[author,time,content,postID,parentID])
     result = cursor.fetchone()
     connection.commit()
     return result

def getComments(connection,postID):
     return connection.execute("SELECT c.*,r.Content as ReplayContent FROM COMMENTS c LEFT JOIN COMMENTS r ON r.ParentID = c.ID WHERE c.PostID = ? AND c.ParentID IS NULL",[postID])


