import secrets,hashlib
from functools import wraps
from flask import g,request,jsonify
from dbHandle import validate_author

def generate_api_key():
    key = secrets.token_urlsafe(32)
    hashed_key = hashlib.sha256(key.encode()).hexdigest()

    return {"key":key, "hashedKey": hashed_key}


#TODO uncomment author to validate using hash
def authenticate(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        key = request.headers.get("Authorization")
        if(not key):
            return jsonify(err="No authorization header"), 400

        key = key.replace("Bearer","").strip()
        author = validate_author(hashlib.sha256(key.encode()).hexdigest())
        #author = validate_author(key)
        

        if(not author):
            return jsonify(err="Unauthorized"), 401
        
        g.author = author[0]
        return f(*args,**kwargs)
    return wrapper