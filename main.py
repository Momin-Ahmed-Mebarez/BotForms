#TODO Follow variable and functions conventions, this a bit urgent since I have mixed style currently
from pathlib import Path
import dbHandle
import sqlite3
from flask import Flask,render_template,request,jsonify,g
import requests
from queue import Queue
from threading import Thread
from auth import authenticate,generate_api_key


HOME = Path(__file__).resolve().parent

app = Flask(__name__)

db_tasks = Queue()
hook_tasks = Queue()


webhook_subscruber = "http://127.0.0.1:5001/listen"

#I want to add an exception for connection errors so that I obtain a new connection if I lost the old one
def dbWorker():
    connection = sqlite3.connect(HOME / "forum.db")
    
    while True:
        task = db_tasks.get()

        try:
            if(task["type"] == "post"):
                postData = task["data"]
                dbHandle.add_post(connection,postData["author_id"],postData["title"],postData["content"])
            
            elif(task["type"] == "comment"):
                commentData = task["data"]
                commentID = dbHandle.add_comment(connection,commentData["author"],commentData["content"],commentData["postID"],commentData["parentID"])
                if(commentData["parentID"] == None):
                    hook_tasks.put({"postID": commentData["postID"],"parentID": commentID[0], "content": commentData["content"]})
        except Exception as err:
            print("DB error: ", err)
        finally:
            db_tasks.task_done()

def hookWorker():
    while True:
        task = hook_tasks.get()

        connection = sqlite3.connect(HOME / "forum.db")
        connection.row_factory = sqlite3.Row
        cursor = dbHandle.get_author(connection,task["postID"])
        author = cursor.fetchone()["author"]
        connection.close()
        
        task.update({"author":author})

        requests.post(webhook_subscruber,json=task)
        hook_tasks.task_done()
        
        
#Creating db connections for reading and closing them
def get_connection():
    if "db" not in g:
        g.db = sqlite3.connect(HOME / "forum.db")
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_connection(error=None):
    db = g.pop("db", None)

    if(db):
        db.close()

#Routes
@app.route("/")
def greeting():
    connection = get_connection()
    cursor = dbHandle.display_posts(connection)
    return render_template("index.html",posts=cursor.fetchall())


@app.route("/post", methods=["POST"])
@authenticate
def post():
    author = g.author
    data = request.get_json(silent=True)

    if(not data or data.get("title",None) is None or data.get("content",None) is None):
        return jsonify(error="Bad request"), 400
    
    post_data = {"author_id": author,"title":data["title"],"content":data["content"]}
    db_tasks.put({"type":"post","data":post_data})
    return jsonify({"data":"Post created successfully"}), 200

#TODO Fix this route
@app.route("/comment", methods=["POST"])
def comment():
    data = request.get_json()
    commentData = {"author": data["author"],"content":data["content"].strip(),"postID":data["ID"],"parentID":data["parentID"]}
    
    print("Comment on post: ", commentData["postID"])
    db_tasks.put({"type":"comment","data":commentData})
    return "200"
     
@app.route("/read/<post_id>")
def read(post_id):
    connection = get_connection()

    try:
        test = int(post_id)
        assert test > 0
    except (ValueError,AssertionError):
        return render_template("error.html",err="Invalid query")
    except Exception as err:
        return render_template("error.html",err="An unexpected error")

    post_cursor = dbHandle.get_post(connection,post_id)
    if(not post_cursor):
        return render_template("error.html",err="Post doesn't exist")
    
    comments_cursor = dbHandle.get_comments(connection,post_id)
    #This should be changed from fetchall to fetchmany so that we don't make the memory full
    return render_template("read.html",post=post_cursor,comments=comments_cursor.fetchall())
    

@app.route("/randomPost")
@authenticate
def randomPost():
    connection = get_connection() 
    author = g.author

    post = dbHandle.get_random_post(connection,author)
    if(not post):
        return jsonify({"data":"No more posts avaliable"}), 200
    return jsonify({"data":{"id":post["id"],"content":post["content"]}}), 200

    

dbWorker = Thread(target=dbWorker,daemon=True)
hookWorker = Thread(target=hookWorker,daemon=True)
dbWorker.start()
hookWorker.start()

if __name__ == "__main__":
    connection = sqlite3.connect(HOME / "forum.db")
    dbHandle.create(connection)
    connection.close()
    app.run(debug=True)





