from app import mongo
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    @staticmethod
    def find_user_by_email(email):
        return mongo.db.users.find_one({"email": email}, {"_id": 0})

    @staticmethod
    def insert_user(email, password):
        hashed_password = generate_password_hash(password)
        return mongo.db.users.insert_one({"email": email, "password": hashed_password})

    @staticmethod
    def verify_password(email, password):
        user = mongo.db.users.find_one({"email": email})
        if not user:
            return False
        return check_password_hash(user["password"], password)
