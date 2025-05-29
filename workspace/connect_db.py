import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

uri = os.environ["MONGO_URI"].replace("<db_password>", os.environ["MONGO_PW"])

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    users = client["SSHS-Matcher"]["User"]
    rooms = client["SSHS-Matcher"]["Room"]
except Exception as e:
    print(e)
