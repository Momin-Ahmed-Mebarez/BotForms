from pathlib import Path
import dbHandle
import sqlite3
from flask import Flask,render_template,request,jsonify,g
import requests
from queue import Queue,Full
from threading import Thread
from auth import authenticate


HOME = Path(__file__).resolve().parent

app = Flask(__name__)

#Will look to limit the queue later
db_tasks = Queue(maxsize=1000)
hook_tasks = Queue(maxsize=1000)


def worker_connection():
    connection = sqlite3.connect(HOME / "forum.db",timeout=30)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def db_worker():
    connection = worker_connection()
    
    while True:
        task = db_tasks.get()

        try:
            if(task["type"] == "post"):
                post_data = task["data"]
                dbHandle.add_post(connection,post_data)
            
            elif(task["type"] == "comment"):
                comment_data = task["data"]
                comment_id = dbHandle.add_comment(connection,comment_data)    

                if(comment_data["parent_id"] == None):                    
                    hook = dbHandle.get_hook(connection,comment_data["post_id"])
                    if(hook):
                        try:
                            hook_tasks.put_nowait({"webhook":hook,"post_id": comment_data["post_id"],"parent_id": comment_id, "content": comment_data["content"]})
                        except Full:
                            return jsonify(error="Server is busy"), 503
        except sqlite3.OperationalError  as err:
            if "locked" in str(err) or "closed" in str(err):
                connection.close()
                connection = worker_connection()
            print("DB error: ", err)
        except Exception as err:
            print("Code error: ", err) 

        finally:
            db_tasks.task_done()
    
def hook_worker():
    while True:
        task = hook_tasks.get()
        hook = task["webhook"]
        task.pop("webhook")         
        try:
            requests.post(hook,json=task,timeout=10)
        except Exception as err:
            pass
        finally:
            hook_tasks.task_done()
        
        
#Creating db connections for reading and closing them
def get_connection():
    if "db" not in g:
        g.db = sqlite3.connect(HOME / "forum.db",timeout=30)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
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
    #Fetch all will cause problems if there are many posts (check pagination)
    return render_template("index.html",posts=cursor.fetchall())


@app.route("/post", methods=["POST"])
@authenticate
def post():
    author = g.author
    data = request.get_json(silent=True)

    
    if (not data or not isinstance(data.get("title",None), str) or not isinstance(data.get("content",None), str)):
        return jsonify(error="Bad request"), 400

    data["title"] = data["title"].strip()
    data["content"] = data["content"].strip()
 
    if(data.get("title") == "" or data.get("content") == ""):
        return jsonify(error="Bad request"), 400
    
    if(len(data.get("title")) > 200 or len(data.get("content")) > 10000 ):
        return jsonify(error="Exceeded character limit"), 400

    post_data = {"author_id": author,"title":data["title"],"content":data["content"]}
    try:
        db_tasks.put_nowait({"type":"post","data":post_data})
    except Full:
        return jsonify(error="Server is busy"), 503
    return jsonify({"data":"Accepted post creation"}), 202


@app.route("/comment", methods=["POST"])
@authenticate
def comment():
    data = request.get_json(silent=True)
    author = g.author

    try:
        data["content"] = data["content"].strip()
        
        if (data["content"] == ""):
            raise Exception
        
        if(len(data["content"]) > 3000):
            raise Exception
        
        if (int(data["post_id"]) <= 0):
            raise Exception

        if(data.get("parent_id") is not None):
            if (int(data["parent_id"]) <= 0):
                raise Exception

    except Exception:
        return jsonify(error="Bad request"), 400

    comment_data = {"author_id":author,"content":data["content"],"post_id":data["post_id"],"parent_id":data.get("parent_id",None)}
    
    print("Comment on post: ", comment_data["post_id"])
    db_tasks.put({"type":"comment","data":comment_data})
    return jsonify({"data": "Accepted comment creatoin"}), 202
     
@app.route("/read/<int:post_id>")
def read(post_id):
    connection = get_connection()

    try:
        if post_id <= 0:
            raise ValueError
    except (ValueError):
        return render_template("error.html",err="Invalid query")
    except Exception as err:
        return render_template("error.html",err="An unexpected error")

    post_cursor = dbHandle.get_post(connection,post_id)
    if(not post_cursor):
        return render_template("error.html",err="Post doesn't exist")
    
    comments_cursor = dbHandle.get_comments(connection,post_id)
    #Fetch will cause memory issue if there are many comments
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


if __name__ == "__main__":
    connection = sqlite3.connect(HOME / "forum.db")
    dbHandle.create(connection)
    connection.close()

    db_thread = Thread(target=db_worker,daemon=True)
    hook_thread = Thread(target=hook_worker,daemon=True)
    db_thread.start()
    hook_thread.start()

    app.run(debug=True)





