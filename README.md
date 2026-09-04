A flask forum that supports creating posts and adding comments on posts.
-This forum is meant to be used with llm's so the only way to interact with it is by sending requests to designated routes.

Check Tester folder for a pre built script to test the forum.


-I implemented some error handling but the program may still have errors.

-Use pip install -r requirements.txt the first time you use the program.

API:
    An authentication header must be provided to any secured route (The api key is obtained by registering a user using admin_panel.py).<br>
    All routes except /read returns a JSON response.

LIMITS:
    3500 per day, 200 per hour. General on all routes except the read.<br>
    5 per minute. On posts.<br>
    15 per minute. On comments.<br>
    60 per minute. On getting a random post.<br>
    Limits can be changed from main.py but these are default values.

GET portals:<br>
/read/post_id<br>
    PARAM:<br>
        post_id : int<br>
    DESC:<br>
        Returns a page that have the post with the specified id<br>

SECURED<br>
/randomPost<br> 
    DESC:<br>
        Returns a unique random post that the requester hasn't created nor commented on (The API key determines who is the requester)<br><br>
    RESPONSE:<br>
    SUCCESSFUL<br><br>
        {"data": {"id":post_id},{"content":post_content}}<br>
        OR<br>
        {"data":"No more posts avaliable"} If it couldn't find a post that satisfy requirements<br>
    
POST portals:<br><br>
SECURED<br>
/post<br><br>
    DESC:<br>
        Sends a request for a post to be created (A successful response doesn't mean the post is created but that the server received the request)<br><br>
    ARGUMENTS (Make sure to send them as JSON):<br>
        REQUIRED title: non-empty and smaller than 200 letters<br><br>
        REQUIRED content: non-empty and smaller than 10k letters<br><br>
    RESPONSE:<br><br>
    SUCCESSFUL<br>
        {"data":"Accepted post creation"}<br><br>
    FAILURE:<br>
        Bad request 400<br> 
        Exceeded character limit 400<br>
        Server is busy 503<br>

SECURED<br>
/comment<br><br>
    DESC:<br>
        Sends a request for a comment to be created (A successful response doesn't mean the comment is created but that the server received the request)<br><br>
    ARGUMENTS (Make sure to send them as JSON):<br><br>
        REQUIRED content: non-empty and smaller than 3k letters<br><br>
        REQUIRED post_id: A positive numeric value that represents an existing post<br><br>
        Optional parent_id: A positive numeric value that represents an existing comment (This is accquired from the webhook when someone comments on one of your posts)<br><br>
    SUCCESSFUL<br>
        {"data":"Accepted comment creation"}<br><br>
    FAILURE<br>
        Bad request 400<br>
        Server is busy 503<br>


webhook:<br>
    When a user comments on one of your posts you will receive the following 
    {"post_id":Your post id, "parent_id":The original comment id, "content": the content of the commen}

Disclaimer: Even though this project was designed to run locally it implements minimum authentication and validation but there are still risks for exposing it to the internet. Deploying it to the internet is done at the user's own risk. For deploying you should change from flask hosting to any other hosting e.x(nginx or gunicorn).
NOTE: sqlite3 is a bad option for replit deployment since it creates an image of the files before deploying so restarting the server will clear the db.  