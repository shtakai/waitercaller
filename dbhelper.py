import pymongo

DATABASE = "waitercaller"


class DBHelper:

    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client[DATABASE]

    def get_user(self, email):
        return self.db.users.find_one({"email": email})

    def add_user(self, email, salt, hashed):
        self.db.users.insert(
            {
                "email": email,
                "salt": salt,
                "hashed": hashed
            }
        )
