from pathlib import Path
import dbHandle
import sqlite3
from flask import Flask,render_template,request,jsonify,g
from queue import Queue
from threading import Thread

HOME = Path(__file__).resolve().parent

app = Flask(__name__)

taskQueue = Queue()

def worker():
    connection = sqlite3.connect(HOME / "forum.db")
    
    while True:
        task = taskQueue.get()

        try:
            if(task["type"] == "post"):
                postData = task["data"]
                dbHandle.addPost(connection,postData["author"],postData["title"],postData["content"])
            elif(task["type"] == "comment"):
                commentData = task["data"]
                dbHandle.addComment(connection,commentData["author"],commentData["content"],commentData["ID"])
        except Exception as err:
            print("DB error: ", err)
        finally:
            taskQueue.task_done()

def get_connection():
    if "db" not in g:
        g.db = sqlite3.connect(HOME / "forum.db")
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
    connection.row_factory = sqlite3.Row
    cursor = dbHandle.displayPosts(connection)
    return render_template("index.html",posts=cursor.fetchall())


@app.route("/post", methods=["POST"])
def post():
    data = request.get_json()
    postData = {"author": data["author"],"title":data["title"],"content":data["content"]}
    taskQueue.put({"type":"post","data":postData})
    return "200"

@app.route("/comment", methods=["POST"])
def comment():
    data = request.get_json()
    commentData = {"author": data["author"],"content":data["content"].strip(),"ID":data["ID"]}
    print(commentData["content"])
    print("Comment on post: ", commentData["ID"])
    taskQueue.put({"type":"comment","data":commentData})
    return "200"

#TODO Validate the id to stop weird behaviour       
@app.route("/read/<post_id>")
def read(post_id):
    connection = get_connection()
    connection.row_factory = sqlite3.Row
    postCursor = dbHandle.getPost(connection,post_id)
    commentsCursor = dbHandle.getComments(connection,post_id)
    return render_template("read.html",post=postCursor.fetchone(),comments=commentsCursor.fetchall())

@app.route("/randomPost")
def randomPost():
    author = request.args.get("author",default=None)
    connection = get_connection()
    cursor = dbHandle.getRandomPost(connection,author)
    return jsonify({"data":cursor.fetchone()}), "200"

    

thread = Thread(target=worker,daemon=True)
thread.start()

if __name__ == "__main__":
    connection = sqlite3.connect(HOME / "forum.db")
    dbHandle.create(connection)
    connection.close()
    app.run(debug=True)





