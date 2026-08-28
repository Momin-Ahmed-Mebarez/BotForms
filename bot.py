import requests,time
from threading import Thread
from pathlib import Path

#TODO Add proper error handling
#TODO Add a cause to request a new connection if it was lost

class Bot:
    API = "http://localhost:11434/api/chat"
    URL = "http://127.0.0.1:5000/"
    SCRIPT_DIR = Path(__file__).resolve().parent
    INSTRUCTIONS_FILE = SCRIPT_DIR / "instructions.txt"
#qwen3.5:4b
#qwen3:1.7b
    def __init__(self,name: str,module="qwen3:1.7b",thinker=True):
        self.name = name
        self.module = module
        self.thinker = thinker
        
        self.tasks = []
        self.working = False
        self.readInstructions()

    def recvMsg(self,msg):
        self.addToQueue(msg)
        if(not self.working):
            self.working = True
            t = Thread(target=self.work)
            t.start()

    def addToQueue(self,msg):
        if("<CREATE>" not in msg["content"] and "<COMMENT>" not in msg["content"]):
            self.tasks.append(msg)
        elif(len(self.tasks) == 0):
            self.tasks.append(msg)

    #I think I can use self.tasks.pop() instead of self.tasks[0]
    def work(self):
        while len(self.tasks) > 0:
            msg = self.tasks[0]["content"]
            aiParams = {"model":self.module,
            "messages":[{"role":"system", "content": self.instructions}] + [{"role":"user", "content": msg}],
            "think" : self.thinker,
            "stream": False,}
            resp = requests.post(self.API,json=aiParams).json()["message"]["content"]
            
            apiParams = {"author": self.name, "title": resp.split("\n")[0]}
            if("<CREATE>" in msg):
                apiParams.update({"content": "".join(resp.split("\n")[1:])})        
                requests.post(self.URL + "post",json=apiParams)
            elif("<COMMENT>" in msg):
                 apiParams.update({"content": resp,"ID" :self.tasks[0]["ID"]})
                 requests.post(self.URL + "comment",json=apiParams)
            self.tasks.pop(0)
        self.working = False




    """"
    def reading(self):
        if(not self.working):
            self.working = True
            t = Thread(target=self.work)
            t.start()
        else:
            self.addTask()

        
    def work(self):
        while(len(self.tasks) > 0):
            print(self.tasks)
            self.tasks.pop(0)
            time.sleep(4)
        self.working = False

    def addTask(self):
        self.tasks.append(0)

    """
    def readInstructions(self):
        with open(self.INSTRUCTIONS_FILE,"r") as f:
            self.instructions = f.read()