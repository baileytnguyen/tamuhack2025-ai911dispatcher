from pymongo import MongoClient
import pymongo
import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials from environment variables
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
cluster_name = os.getenv("MONGO_CLUSTER")
database_name = os.getenv("MONGO_DATABASE")

# MongoDB Atlas connection string
connection_string = f"mongodb+srv://{username}:{password}@{cluster_name}.74tfh.mongodb.net/"

# Create a MongoDB client
client = MongoClient(connection_string)

# Connect to the specified database
db = client[database_name]

# Define the collection (table) name where you want to insert data
collection_name = "emergency_data"  # Replace with the name of your collection
sequence_collection_name = "sequence"  # Collection to store the serial number sequence
collection = db[collection_name]
sequence_collection = db[sequence_collection_name]

# Function to get and increment the serial ID
def get_next_serial_id():
    sequence = sequence_collection.find_one_and_update(
        {"_id": "serial_id"},  # We will use _id = "serial_id" to track this counter
        {"$inc": {"seq": 1}},  # Increment the "seq" field by 1
        upsert=True,  # If the document doesn't exist, create it
        return_document=pymongo.ReturnDocument.AFTER  # Return the updated document
    )
    return sequence["seq"]

# Function to collect input data from the user
def collect_input_data():
    # Collect data from the user based on the given inputs
    name = input("Enter the caller's name: ")
    location = input("Enter the location: ")
    phone_number = input("Enter the phone number: ")
    situation = input("Describe the situation: ")
    priority = int(input("Enter the priority level (1-4): "))  # Example: 1 (low) to 5 (high)
    missing_information = input("Is there any missing information? (true/false): ").lower() == "true"
    question_to_ask = input("Is there a question to ask? (leave blank if none): ")
    extra_notes = input("Any extra notes?: ")
    status = input("Status on issue: ")

    # Get the next available serial ID
    serial_id = get_next_serial_id()

    # Create a dictionary with the collected data, including the serial ID
    data_to_insert = {
        "_id": serial_id,  # Use the serial ID as the unique identifier
        "name": name,
        "location": location,
        "phone_number": phone_number,
        "situation": situation,
        "priority": priority,
        "missing_information": missing_information,
        "question_to_ask": question_to_ask,
        "date" : datetime.datetime.today(),
        "extra_notes": extra_notes,
        "status": status
    }

    return data_to_insert

# Collect input data
data_to_insert = collect_input_data()

# Insert the data into the collection
inserted_data = collection.insert_one(data_to_insert)

# Output the inserted data's unique ID (from the _id field)
print(f"Data inserted with serial ID: {data_to_insert['_id']}")
