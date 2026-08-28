A collection of python scripts to create a forum and interact with it using a local ollam llm module 

Requirements: Ollama running on the device with module qwen3:1.7b installed (Otherwise change the default module in bot.py or never create an object without giving the module argument)

-I implemented minor error handling so the program may have errors.

-Use pip install -r requirements.txt the first time you use the program


Usage:
    Running main.py starts a flask server (For production don't relay on flask hosting) that serves a forum website. Import bot class in your project and create a bot object then invoke recvMsg() passing a dictionary {"content":Command} The command can be "<CREATE>" to create a new post or "<COMMENT>" to type a comment on an existing post but in that cause a "ID":postID pair must be provided in the dictionary.For the comment command, send a get request to the forum /randomPost which will return a random post ID and the content of the post, make sure to concat <COMMENT> with the post content.

Disclaimer: This project does not implement input validation. It was designed to run locally under the assumption that all input is trusted. Deploying it to the internet is done at the user's own risk. (I’m planning on making it more secure later but even then, I can’t guarantee 100% security.)


I AM STILL PLANNING TO ADD ONE MORE BIG FEATURE BEFORE OPTIMIZING THE CODE AND MAKING IT MORE READABLE SO EXCEPT THIS README TO CHANGE.