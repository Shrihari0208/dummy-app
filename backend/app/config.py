from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://shriharideshmukh382:E2MQHFED73OivUdd@cluster0.uqvxu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
