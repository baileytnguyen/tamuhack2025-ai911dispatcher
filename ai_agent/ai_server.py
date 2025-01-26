import grpc
from concurrent import futures
from prompt import mainDirectives
import ai911dispatcher_pb2
from pymongo import MongoClient
import pymongo
import ai911dispatcher_pb2_grpc
import ai911displaychatdisplay_pb2
import ai911displaychatdisplay_pb2_grpc
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
import os
from playsound import playsound
import datetime
import time

# Get the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
ai_server_port = os.getenv("AI_SERVER_PORT")
ai_server_ip = os.getenv("AI_SERVER_IP")
chatdisplay_server_ip = os.getenv("CHATDISPLAY_SERVER_IP")
chatdisplay_server_port = os.getenv("CHATDISPLAY_SERVER_PORT")
client = OpenAI(api_key=openai_api_key)
load_dotenv()

# Retrieve credentials from environment variables
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
cluster_name = os.getenv("MONGO_CLUSTER")
database_name = os.getenv("MONGO_DATABASE")

# MongoDB Atlas connection string
connection_string = f"mongodb+srv://{username}:{password}@{cluster_name}.74tfh.mongodb.net/"

# Create a MongoDB client
db_client = MongoClient(connection_string)

# Connect to the specified database
db = db_client[database_name]

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

def tts(speech):
    # Load environment variables from .env file
    client = OpenAI()
    speech_file_path = Path(__file__).parent / "speech.mp3"

    # Check if the file exists, and delete it if so
    if speech_file_path.exists():
        os.remove(speech_file_path)
        print(f"Deleted existing file: {speech_file_path}")

    # Generate new speech file
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=speech,
    )
    
    # Save the speech file to the specified path
    response.stream_to_file(speech_file_path)
    print(f"New speech file created: {speech_file_path}")
    
    return speech_file_path


def parse_llm_output(output):
    parsed_data = {}
    
    # Split the output by lines and process each line
    lines = output.strip().split('\n')
    
    for line in lines:
        # Split each line into key and value
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # Add the key-value pair to the parsed_data dictionary
        parsed_data[key] = value
    
    return parsed_data

# Implementing the service methods
class MainServiceServicer(ai911dispatcher_pb2_grpc.MainServiceServicer):

    def InitiateSession(self, request, context):
        # Handle the InitiateSession RPC call
        print(f"Session initiated for phone number: {request.phoneNum}")
        return ai911dispatcher_pb2.SuccessCode(status="Session initiated successfully.")

    def SendCallerResponse(self, request, context):
        # Handle the SendCallerResponse RPC call
        print(f"Caller response received: {request.Response}")

        message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content= request.Response
        )

        run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        )

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list( thread_id=thread.id)
            if messages.data:
                content = messages.data[0].content[0].text.value
                print("LLMOUTPUT: \n"+content)
                LLMResponse = content
                # Convert the data into a dictionary
                parsed_data = {}
                for line in content.strip().splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        parsed_data[key.strip()] = value.strip() if value.strip() else None

                # Access specific fields
                print(f"Missing Information: {parsed_data.get('missing_information')}")
                print(f"Question to Ask: {parsed_data.get('question_to_ask')}")
                print(f"Situation: {parsed_data.get('situation')}")
                
                # publish content to chat display
                display_msg = ai911displaychatdisplay_pb2.PublishMessageRequest(role="Assistant",contents=parsed_data.get('question_to_ask'),time="latest")
                display_success = display_stub.PublishMessage(display_msg)
                
                # if missing information, ask question, else if not, push to database
                if parsed_data.get('missing_information').lower() == 'true':
                    print("Missing information found. Asking question...")
                    # Call text to speech functionality
                    response = client.audio.speech.create(
                        model="tts-1",
                        voice="nova",
                        input=parsed_data.get('question_to_ask'),
                    )
                    speech_file_path = tts(parsed_data.get('question_to_ask'))
                    file_path = os.path.normpath(speech_file_path)
                    time.sleep(3)
                    playsound(file_path)
                elif (parsed_data.get('missing_information').lower() == 'false'):
                    # Create a dictionary with the collected data, including the serial ID
                    serial_id = get_next_serial_id()
                    data_to_insert = {
                        "_id": serial_id,  # Use the serial ID as the unique identifier
                        "name": parsed_data.get('name'),
                        "location": parsed_data.get('location'),
                        "phone_number": parsed_data.get('phone_number'),
                        "situation": parsed_data.get('situation'),
                        "priority": parsed_data.get('priority'),
                        "missing_information": parsed_data.get('missing_information'),
                        "question_to_ask": "",
                        "date" : datetime.datetime.today(),
                        "extra_notes": parsed_data.get('extra_notes'),
                        "status": "Open"
                    }
                    inserted_data = collection.insert_one(data_to_insert)
                    
                    # clear memory
                    inputResponse = ""
                    LLMResponse = ""

                
                
            else:
                print("No messages received.")
        else:
            print("wowie wow")

        # create global var
        # store in global var the request.Response and 
        # LLMOUTPUT for future feed again
        inputResponse = request.Response
        
        # Extract data from llm output
        # If missing, call text to speech functionality

        #if bool(parsedData[missing_information]) == True:
        # content
            
        # Wait for response ( max 30 secs )
        # if complete, create db oject and store
        # if expire too long, create object and store    

        return ai911dispatcher_pb2.SuccessCode(status="Caller response processed successfully.")

    def EndSession(self, request, context):
        # Handle the EndSession RPC call
        print(f"Ending session for phone number: {request.phoneNum}")
        return ai911dispatcher_pb2.SuccessCode(status="Session ended successfully.")

# Function to start the server
def serve():
    # Create the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the servicer to the server
    ai911dispatcher_pb2_grpc.add_MainServiceServicer_to_server(MainServiceServicer(), server)
    
    # Specify the port where the server will listen
    server.add_insecure_port(f'[::]:{ai_server_port}')
    print(f"Server running on port {ai_server_port}...")
    
    # Start the server
    server.start()
    
    # Keep the server running
    server.wait_for_termination()

speech_file_path = Path(__file__).parent / "speech.mp3"

assistant = client.beta.assistants.create(
name="911 Emergency Dispatch Assistant_A",
instructions= mainDirectives,
model="gpt-4o",
)
thread = client.beta.threads.create()

inputResponse = ""
LLMResponse = ""

display_channel = grpc.insecure_channel(f"{chatdisplay_server_ip}:{chatdisplay_server_port}")
display_stub = ai911displaychatdisplay_pb2_grpc.Ai911DispatcherChatDisplayStub(display_channel)

# Entry point for the server
if __name__ == '__main__':
    serve()
