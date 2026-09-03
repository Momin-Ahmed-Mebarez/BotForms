from datetime import datetime
from pathlib import Path
import sqlite3


HOME = Path(__file__).resolve().parent

def create(connection):
    with open(HOME / "schema.sql","r") as f:
         script = f.read()
    connection.executescript(script)

def drop_all_tables(connection):
     """
     Using executescript and dropping all tables with one statement is a better approach, but
     this is better for debugging. 
     """
     connection.execute("DROP TABLE comments")
     connection.execute("DROP TABLE posts")
     connection.execute("DROP TABLE authors")
     
     
#Author related
def get_hook(connection,post_id):
     curs = connection.execute("SELECT a.webhook FROM posts p JOIN authors a ON a.id = p.author_id WHERE p.id = ?",[post_id])
     return curs.fetchone()[0]

#POST Related 
def display_posts(connection):
     return connection.execute("SELECT a.name as author,p.id,p.date,p.title FROM posts p JOIN authors a ON p.author_id = a.id")

def get_post(connection,post_id):
     cursor = connection.execute("SELECT a.name as author,p.date,p.title,p.content FROM posts p JOIN authors a ON p.author_id = a.id WHERE p.id = ?",[post_id])
     return cursor.fetchone()


def get_random_post(connection,author_id):
     cursor = connection.execute("SELECT p.id,p.content FROM posts p WHERE p.author_id != ? AND NOT EXISTS(SELECT 1 FROM comments c where c.author_id = ? and c.post_id = p.id) ORDER BY RANDOM() LIMIT 1",[author_id] * 2)
     return cursor.fetchone()
     
     #Deprecated
     #if(author): return connection.execute("SELECT id,content FROM posts p WHERE author != ? AND NOT EXISTS(SELECT 1 FROM comments c WHERE c.author = ? and c.post_id == p.id) ORDER BY RANDOM() LIMIT 1",[author,author])


def add_post(connection,post_data):
     stamp = datetime.strftime(datetime.now(),"%d %b %Y-%H:%M")
     post_data.update({"date":stamp})
     try:
          connection.execute("INSERT INTO posts (author_id,date,title,content) VALUES (:author_id,:date,:title,:content);",post_data)
          connection.commit()
     except sqlite3.Error as err:
          connection.rollback()
          raise sqlite3.DatabaseError("Couldn't create post") from err

#Comment related

def add_comment(connection,comment_data):
     stamp = datetime.strftime(datetime.now(),"%d %b %Y-%H:%M")
     comment_data.update({"date": stamp})
     
     try:
          if(comment_data["parent_id"]):
               cursor = connection.execute("INSERT INTO comments (author_id,date,content,post_id,parent_id) SELECT :author_id,:date,:content,:post_id,:parent_id  WHERE EXISTS (SELECT 1 FROM posts p JOIN comments c ON c.id = :parent_id WHERE p.id = :post_id AND p.author_id = :author_id AND c.post_id = :post_id AND c.parent_id IS NULL) RETURNING id;",comment_data)
          else:
               cursor = connection.execute("INSERT INTO comments (author_id,date,content,post_id,parent_id) VALUES (:author_id,:date,:content,:post_id,:parent_id) RETURNING id;",comment_data)
          result = cursor.fetchone()
          if(not result):
               connection.rollback()
          else:
               connection.commit()
     except sqlite3.Error as err:
          connection.rollback()
          print(err)
          raise sqlite3.DatabaseError("Couldn't add comment") from err
     
     return result

def get_comments(connection,postID):
     return connection.execute("SELECT a.name as author,c.id,c.post_id,c.parent_id,c.content,c.date,r.content as replay_content FROM comments c JOIN authors a ON a.id = c.author_id LEFT JOIN comments r ON r.parent_id = c.ID WHERE c.post_id = ? AND c.parent_id IS NULL",[postID])



#Security related 
def validate_author(api_key):
     connection = sqlite3.connect(HOME / "forum.db")
     try:
          author = connection.execute("SELECT id from authors where api_key = ?",[api_key]).fetchone()
     except Exception as err:
          raise ValidationError("Error while validating user") from err
     finally:
          connection.close()     

     return author

#Admin related
def register_author(connection,name,hashed_key,webhook=None):
     try:
          connection.execute("INSERT INTO authors (name,api_key,webhook) VALUES (:name,:api_key,:webhook)",{"name":name,"api_key":hashed_key,"webhook":webhook})
          connection.commit()
     except Exception as err:
          connection.rollback()
          raise AuthorCantBeRegisteredError(err)

#Helper

"""
def get_author_id_from_name(connection,name):
     author = connection.execute("SELECT id from authors where name = ?",[name]).fetchone()
     if(author):
          return author["id"]
     raise AuthorNotFoundException(f"{name} isn't a registered user")
"""

#Error classes
#Currently not used since it was used with get_author_id_from_name
class AuthorNotFoundException(Exception):
     pass

class ValidationError(Exception):
     pass

class AuthorCantBeRegisteredError(Exception):
     pass