#This script is used to utlize the bot class, feel free to use it to test the project or create your own utlizing the bot class 
import requests,random,os
from bot import Bot
from flask import Flask,request
from threading import Thread
from queue import Queue
from dotenv import load_dotenv

load_dotenv() #Comment if you don't plan on using .env file

#Replace with your token (Use .env file if you plan to host the invoker)
agent0 = Bot(os.getenv("AGENT0_TOKEN"),module="qwen3.5:4b")
agent1 = Bot(os.getenv("AGENT1_TOKEN"),module="qwen3.5:4b")
agent2 = Bot(os.getenv("AGENT2_TOKEN"),module="qwen3.5:4b")
agent3 = Bot(os.getenv("AGENT3_TOKEN"),module="qwen3.5:4b")

agents_list = [agent0,agent1,agent2,agent3]

app = Flask(__name__)

tasks = Queue()

def worker():
    while True:
        task = tasks.get()
        msg = task["task"]
        task["agent"].recv_msg({"post_id": msg["post_id"], "parent_id" : msg["parent_id"], "content": "<REPLAY>" + msg["content"]})

        tasks.task_done()



listener = Thread(target=worker,daemon=True)
listener.start()


#This is made for multi bot, change the if statements as you need
@app.route("/listen/<agent>", methods=["POST"])
def listen(agent):
    tasks.put({"task":request.get_json(),"agent":agents_list[int(agent)]})
    return "200"


@app.route("/new")
def create():
    agent = random.choice(agents_list)
    agent.recv_msg({"content": "<CREATE>"})
    return "200"

@app.route("/replay")
def replay():
    agent = random.choice(agents_list)
    api_header = {"Authorization":f"Bearer {agent.token}"}

    resp = requests.get(agent.URL + "randomPost",headers=api_header).json()

    if(resp.get("data",None) is not None and 'No' not in resp['data']):
        agent.recv_msg({"post_id": resp["data"]["id"], "content": "<COMMENT>" + resp["data"]["content"]})
        return "200"
    else:
        agent.recv_msg({"content": "<CREATE>"})
        return "200"
    


if __name__ == "__main__":
    app.run(debug=True,port=5000)
