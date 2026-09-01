import secrets,hashlib

def generate_api_key():
    key = secrets.token_urlsafe(32)
    hashedKey = hashlib.sha256(key.encode()).hexdigest()

    return {"key":key, "hashedKey": hashedKey}