from concurrent import futures
import grpc
from datetime import datetime
import json
from pathlib import Path
import ai911displaychatdisplay_pb2_grpc
import ai911displaychatdisplay_pb2
import dotenv
import os

# Path to the JSON file used for shared messages
MESSAGES_FILE = Path("messages.json")

# Load environment variables from .env file
dotenv.load_dotenv()
chatdisplay_server_ip = os.getenv("CHATDISPLAY_SERVER_IP")
chatdisplay_server_port = os.getenv("CHATDISPLAY_SERVER_PORT")

# Delete the messages.json file if it exists (on each run)
if MESSAGES_FILE.exists():
    os.remove(MESSAGES_FILE)
    print(f"Deleted existing file: {MESSAGES_FILE}")

class Ai911DispatcherChatDisplayServicer(ai911displaychatdisplay_pb2_grpc.Ai911DispatcherChatDisplayServicer):
    def PublishMessage(self, request, context):
        # Load existing messages or start fresh if file is deleted
        if MESSAGES_FILE.exists():
            with open(MESSAGES_FILE, "r") as file:
                messages = json.load(file)
        else:
            messages = []

        # Append the new message
        new_message = {
            "role": request.role,
            "contents": request.contents,
            "time": request.time,
        }
        messages.append(new_message)

        # Write updated messages to the JSON file
        with open(MESSAGES_FILE, "w") as file:
            json.dump(messages, file, indent=4)

        print(f"Message received and logged: {new_message}")
        return ai911displaychatdisplay_pb2.PublishMessageResponse(code="200")  # Success

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ai911displaychatdisplay_pb2_grpc.add_Ai911DispatcherChatDisplayServicer_to_server(
        Ai911DispatcherChatDisplayServicer(), server
    )
    server.add_insecure_port(f'[::]:{chatdisplay_server_port}')
    print(f"gRPC server running on port {chatdisplay_server_port}...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
