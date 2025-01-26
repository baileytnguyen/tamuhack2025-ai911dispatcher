import grpc
from datetime import datetime
import ai911displaychatdisplay_pb2_grpc
import ai911displaychatdisplay_pb2

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = ai911displaychatdisplay_pb2_grpc.Ai911DispatcherChatDisplayStub(channel)
        
        # Send a message
        request = ai911displaychatdisplay_pb2.PublishMessageRequest(
            role="User",
            contents="Hello, this is a test message!",
            time=datetime.now().isoformat()
        )
        response = stub.PublishMessage(request)
        print(f"Response from server: {response.code}")

if __name__ == "__main__":
    run()
