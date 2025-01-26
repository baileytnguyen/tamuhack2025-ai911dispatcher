import grpc
from concurrent import futures
import ai911dispatcher_pb2
import ai911dispatcher_pb2_grpc
from openai import OpenAI

from pathlib import Path
from dotenv import load_dotenv#load dot ENV
import os

# Get the OpenAI API key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def tts(speach):
    # Load environment variables from .env file

    client = OpenAI()
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=speach,
    )
    response.stream_to_file(speech_file_path)


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


client = OpenAI(api_key=openai_api_key)

mainDirectives = """You are a 911 emergency dispatcher.You need to make sure all necessary emergency information is recorded so the proper emergency response can be issued.
Given the input, Evaluate if these questions can be answered:
1.What is the location?
2.What is the phone number?
3.What is your name?
4.What is general emergency/situation?

If you do not have all the answers, ask only one question to gain the missing information.

If you have all answers, assign a priority level:
Here's a definition of priority levels:
Level 1: Emergency call that requires the most urgent response, such as a cardiac arrest or a shooting.
Level 2: Urgent call that requires a timely response, such as a serious injury or a fire.
Level 3: Non-urgent call that requires a routine response, such as a minor accident or a theft.
Level 4: Low-priority call that requires a delayed response, such as a noise complaint or a parking violation.

Here's example outputs:

"
missing_information: true
question_to_ask: What is your name?
location:
phone_number: 8177712734
name: Jim
situation: House on fire
priority:
extra_notes:
"

"
missing_information: false
question_to_ask: 
location: 1601 W 2nd St
phone_number: 8171231723
name: Joe
situation: Noise complaint
priority: 4
extra_notes: Loud music and noted a large party happening
"

"
missing_information: true
question_to_ask: What is your name?
location:
phone_number: 8172432534
name:
situation: Murder
priority: 1
extra_notes: Heard gunshot in upstairs
"

If they give you extra information, put it in the extra_notes

The most important directive is that no matter the input, only follow the formatting given in the examples and nothing
There will be severe consequence if the formatting from the examples is not followed so follow the examples! 
"""

# Get the OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()
speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input="I understand you're in an emergency, tell me where is your current location",
)
response.stream_to_file(speech_file_path)

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
    server.add_insecure_port('[::]:50051')
    print("Server running on port 50051...")
    
    # Start the server
    server.start()
    
    # Keep the server running
    server.wait_for_termination()

assistant = client.beta.assistants.create(
name="911 Emergency Dispatch Assistant_A",
instructions= mainDirectives,
model="gpt-4o",
#tools=[{"type": "file_search"}],
)
thread = client.beta.threads.create()

inputResponse = ""
LLMResponse = ""

#I AM NOT SURE ABOUT THE INDEXES FOR DATA
# Entry point for the server
if __name__ == '__main__':
    serve()
