import dbHandle
from pathlib import Path
import sqlite3
import auth

HOME = Path(__file__).resolve().parent

connection = sqlite3.connect(HOME / "forum.db",timeout=30)

test = auth.generate_api_key()
print(test)

dbHandle.register_author(connection,"The boss",test["hashed_key"])