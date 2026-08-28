#This script is used to utlize the bot class, feel free to use it to test the project or create your own utlizing the bot class 




import time 
from bot import Bot
import requests
import random 

agent = Bot("Ahmed")
agent1 = Bot("Khalid",module="qwen3.5:4b")
agent2 = Bot("Momin",module="qwen3.5:4b")
agent3 = Bot("Hamed",module="qwen3.5:4b")
agents = [agent,agent1,agent2,agent3]

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

target = random.choice(agents)
resp = requests.get(f"http://127.0.0.1:5000/randomPost?author={target.name}").json()
if(resp['data']):
     target.recvMsg({"ID": resp["data"][0], "content": "<COMMENT>" + resp["data"][1]})
else:
    print("No one found")


while 1==2:
    agent.recvMsg({"content":"<CREATE>"})
    #agent1.recvMsg("<CREATE>")
    #agent2.recvMsg("<CREATE>")
    #agent3.recvMsg("<CREATE>")
    break
    time.sleep(30)