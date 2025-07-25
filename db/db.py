import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))

db = client.Unnchai
data_collection = db.Data
chats_collection = db.Chat


## SENSOR DATA AND PREDICTION
def save_data(data):
    result = data_collection.insert_one(data)
    return result.acknowledged


def get_all_data():
    result = data_collection.find({}).sort("timestamp", -1)
    return list(result)


def get_current_data():
    latest_record = data_collection.find().sort("timestamp", -1).limit(1)
    return list(latest_record)


## CHATS
def get_chat(_id):
    document = list(chats_collection.find({"_id": _id}))
    if document:
        return document
    else:
        return False


def update_chat(_id, new_chat):

    if not chats_collection.find_one({"_id" : _id}):
        chats_collection.insert_one({"_id" : _id, "conversation": [
                    {
                        "role": "system",
                        "content": "You are a knowledgeable AI assistant specializing in agriculture, particularly in the context of Nepal. Your role is to provide concise and relevant answers to user queries related to farming practices, crop cultivation, agricultural policies, and challenges faced by farmers in Nepal. Ensure that your responses are tailored to the unique agricultural landscape of Nepal, considering local practices, climate, and economic factors. DONOT answer anything beside Agriculture",
                    }
                ]})

    result = chats_collection.update_one(
        {"_id": _id},
        {"$push": {"conversation": new_chat}}
    )

    return result.acknowledged
