from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://indrajeet:indu0011@cluster0.qstxp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("testme")
collection = db["users"]  # Collection name

# Home Route
@app.route("/")
def home():
    return "Flask App Connected to MongoDB Atlas!"

# Create User (POST)
@app.route("/add_user", methods=["POST"])
def add_user():
    try:
        data = request.json
        if not data or "name" not in data or "email" not in data:
            return jsonify({"error": "Invalid data"}), 400

        user = {"name": data["name"], "email": data["email"]}
        collection.insert_one(user)
        return jsonify({"message": "User added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get Users (GET)
@app.route("/users", methods=["GET"])
def get_users():
    users = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default _id field
    return jsonify(users)

# Delete User (DELETE)
@app.route("/delete_user", methods=["DELETE"])
def delete_user():
    data = request.json
    if not data or "email" not in data:
        return jsonify({"error": "Email required"}), 400

    result = collection.delete_one({"email": data["email"]})
    if result.deleted_count:
        return jsonify({"message": "User deleted"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
