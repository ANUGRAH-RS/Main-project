from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://dbUser:MySecurePass123@cluster0.erkpg.mongodb.net/django_db?retryWrites=true&w=majority&appName=Cluster0")
db = client["django_db"]
collection = db["lic_app_customuser"]

# Fetch all users
users = list(collection.find({}, {"_id": 1, "username": 1, "email": 1}))
print("Users in MongoDB:", users)
