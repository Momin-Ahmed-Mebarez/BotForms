from pathlib import Path
import dbHandle
import sqlite3
from flask import Flask,render_template,request,jsonify,g
import requests
from queue import Queue
from threading import Thread

HOME = Path(__file__).resolve().parent

app = Flask(__name__)

dbTasks = Queue()
hookTasks = Queue()


webhookSubscriber = "http://127.0.0.1:5001/listen"

def dbWorker():
    connection = sqlite3.connect(HOME / "forum.db")
    
    while True:
        task = dbTasks.get()

        try:
            if(task["type"] == "post"):
                postData = task["data"]
                dbHandle.add_post(connection,postData["author"],postData["title"],postData["content"])
            elif(task["type"] == "comment"):
                commentData = task["data"]
                commentID = dbHandle.add_comment(connection,commentData["author"],commentData["content"],commentData["postID"],commentData["parentID"])
                if(commentData["parentID"] == None):
                    hookTasks.put({"postID": commentData["postID"],"parentID": commentID[0], "content": commentData["content"]})
        except Exception as err:
            print("DB error: ", err)
        finally:
            dbTasks.task_done()

def hookWorker():
    while True:
        task = hookTasks.get()

        connection = sqlite3.connect(HOME / "forum.db")
        connection.row_factory = sqlite3.Row
        cursor = dbHandle.get_author(connection,task["postID"])
        author = cursor.fetchone()["author"]
        connection.close()
        
        task.update({"author":author})

        requests.post(webhookSubscriber,json=task)
        hookTasks.task_done()
        
        

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
def post():
    data = request.get_json()
    postData = {"author": data["author"],"title":data["title"],"content":data["content"]}
    dbTasks.put({"type":"post","data":postData})
    return "200"

@app.route("/comment", methods=["POST"])
def comment():
    data = request.get_json()
    commentData = {"author": data["author"],"content":data["content"].strip(),"postID":data["ID"],"parentID":data["parentID"]}
    
    print("Comment on post: ", commentData["postID"])
    dbTasks.put({"type":"comment","data":commentData})
    return "200"

#TODO Validate the id to stop weird behaviour       
@app.route("/read/<post_id>")
def read(post_id):
    connection = get_connection()

    postCursor = dbHandle.get_post(connection,post_id)
    commentsCursor = dbHandle.get_comments(connection,post_id)
    return render_template("read.html",post=postCursor.fetchone(),comments=commentsCursor.fetchall())

@app.route("/randomPost")
def randomPost():
    author = request.args.get("author",default=None)
    connection = get_connection() #The returned connection wasn't a row so check if this breaks something
    cursor = dbHandle.get_random_post(connection,author)
    return jsonify({"data":cursor.fetchone()}), "200"

    

dbWorker = Thread(target=dbWorker,daemon=True)
hookWorker = Thread(target=hookWorker,daemon=True)
dbWorker.start()
hookWorker.start()

if __name__ == "__main__":
    connection = sqlite3.connect(HOME / "forum.db")
    dbHandle.create(connection)
    connection.close()
    app.run(debug=True)





