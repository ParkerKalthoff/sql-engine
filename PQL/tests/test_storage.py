from sql_engine.storage import *

db = Database()
db.create_table("users", {"id": "INT", "name": "TEXT", "email": "TEXT"})

users = db.get_table("users")

users.insert({
    "id": ["1", "2"],
    "name": ["Alice", "Bob"]
})

print(users.data)
users.insert({
    "id": ["3"],
    "name": ["Charlie"],
    "email": ["charlie@example.com"]
})

print(users.data)
