import requests
from threading import Thread
from queue import Queue
from pathlib import Path

#Avaliable modules (I am using these to keep track of names this comment can be removed)
    #qwen3.5:4b
    #qwen3:1.7b

class Bot:
    API = "http://localhost:11434/api/chat" #This is the url for the modules 
    URL = "https://bot-forums--momin-ahmed.replit.app/" #This is the url for the forums site
    LOCAL_URL = "" #"http://127.0.0.1:5000/" Uncomment for local testing 

    SCRIPT_DIR = Path(__file__).resolve().parent
    INSTRUCTIONS_FILE = SCRIPT_DIR / "instructions.txt" #File containing bot instructions 

    def __init__(self,token,module="qwen3:1.7b",thinker=True):
        self.token = token
        self.module = module
        self.thinker = thinker
        
        self.tasks = Queue()
        t = Thread(target=self.work, daemon=True)
        t.start()

        self.read_instructions()

    def recv_msg(self,msg):
        #self.tasks.put(msg)
        
        #Comment this and uncomment the self.tasks.put(msg) if you don't want to give priority to replays on comments made on a post
        if("<CREATE>" not in msg["content"] and "<COMMENT>" not in msg["content"]):
            print("A replay was put for handeling")
            self.tasks.put(msg)
            return "Message added successfully"
        elif(self.tasks.empty()):
            self.tasks.put(msg)
            return "Message added successfully"
        

    def work(self):
        while True:
            task = self.tasks.get()
            msg = task["content"]

            ai_params = {"model":self.module,
            "messages":[{"role":"system", "content": self.instructions}] + [{"role":"user", "content": msg}],
            "think" : self.thinker,
            "stream": False,}

            resp = requests.post(self.API,json=ai_params).json()["message"]["content"]
            
            api_header = {"Authorization":f"Bearer {self.token}"}
            api_params = {"title": resp.split("\n")[0]}
            
            if("<CREATE>" in msg):
                api_params.update({"content": "".join(resp.split("\n")[1:])})        
                site_resp = requests.post(self.URL + "post",headers=api_header,json=api_params)
           
            elif("<COMMENT>" or "<REPLAY>" in msg):
                 api_params.update({"content": resp,"post_id" :task["post_id"],"parent_id":task.get("parent_id",None)})
                 print(api_params)
                 requests.post(self.URL + "comment",headers=api_header,json=api_params)
            
            self.tasks.task_done()

    def read_instructions(self):
        with open(self.INSTRUCTIONS_FILE,"r") as f:
            self.instructions = f.read()
