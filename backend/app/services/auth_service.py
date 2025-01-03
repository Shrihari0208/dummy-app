from app.models.user_model import UserModel

def register_user(email, password):
    existing_user = UserModel.find_user_by_email(email)
    if existing_user:
        raise ValueError("User already exists")
    UserModel.insert_user(email, password)
    return {"message": "User registered successfully"}

def login_user(email, password):
    if not UserModel.verify_password(email, password):
        raise ValueError("Invalid email or password")
    return {"message": "Login successful"}

def check_user_exist(email):
    user = UserModel.find_user_by_email(email)
    return {"exists": bool(user)}
