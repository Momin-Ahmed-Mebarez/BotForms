import requests,time
from threading import Thread
from queue import Queue
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
        
        self.tasks = Queue()
        t = Thread(target=self.work, daemon=True)
        t.start()

        self.readInstructions()

    def recvMsg(self,msg):
        """
        #Uncomment this and comment the self.tasks.put(msg) if you want to give priority to replays on comments made on a post
        if("<CREATE>" not in msg["content"] and "<COMMENT>" not in msg["content"]):
            self.tasks.put(msg)
            return "Message added successfully"
        elif(self.tasks.empty()):
            self.tasks.put(msg)
            return "Message added successfully"
        """

        self.tasks.put(msg)


    def work(self):
        while True:
            task = self.tasks.get()
            msg = task["content"]

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
                 apiParams.update({"content": resp,"ID" :task["ID"]})
                 requests.post(self.URL + "comment",json=apiParams)
            self.tasks.task_done()




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