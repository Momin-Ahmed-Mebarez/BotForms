#This script is used to utlize the bot class, feel free to use it to test the project or create your own utlizing the bot class 
import requests,random,time 
from LABS.BotForms.Tester.bot import Bot
from flask import Flask,request
from threading import Thread
from queue import Queue



agent0 = Bot("Ahmed",module="qwen3.5:4b")
agent1 = Bot("Khalid",module="qwen3.5:4b")
agent2 = Bot("Momin",module="qwen3.5:4b")
agent3 = Bot("Hamed",module="qwen3.5:4b")
agents = [agent0,agent1,agent2,agent3]

app = Flask(__name__)

tasks = Queue()

def worker():
    while True:
        task = tasks.get()
        for agent in agents:
            if(agent.name == task["author"]):
                print(f"Sending to {agent.name}")
                agent.recvMsg({"ID": task["postID"], "parentID" : task["parentID"], "content": "<REPLAY>" + task["content"]})

        tasks.task_done()



listener = Thread(target=worker,daemon=True)
listener.start()



@app.route("/listen", methods=["POST"])
def listen():
    tasks.put(request.get_json())
    return "200"


@app.route("/new")
def create():
    agent = random.choice(agents)
    agent.recvMsg({"content": "<CREATE>"})
    return "200"

@app.route("/replay")
def replay():
    agent = random.choice(agents)
    resp = requests.get(f"http://127.0.0.1:5000/randomPost?author={{agent.name}}").json()

    if(resp['data']):
        agent.recvMsg({"ID": resp["data"][0], "content": "<COMMENT>" + resp["data"][1]})
        return "200"
    else:
        return "404"
    


if __name__ == "__main__":
    app.run(debug=True,port=5001)






"""
while True:
    target = random.choice(agents)
    target = "Momin"
    resp = requests.get(f"http://127.0.0.1:5000/randomPost?author={{target.name}}").json()
    if(resp['data']):
        print(resp)
    else:
        print("No one found")
    time.sleep(10)
"""

"""
target = random.choice(agents)
resp = requests.get(f"http://127.0.0.1:5000/randomPost?author={target.name}").json()
if(resp['data']):
     target.recvMsg({"ID": resp["data"][0], "content": "<COMMENT>" + resp["data"][1]})
     time.sleep(99999999999)
else:
    print("No one found")


while 1==2:
    agent.recvMsg({"content":"<CREATE>"})
    #agent1.recvMsg("<CREATE>")
    #agent2.recvMsg("<CREATE>")
    #agent3.recvMsg("<CREATE>")
    break
    time.sleep(30)
"""