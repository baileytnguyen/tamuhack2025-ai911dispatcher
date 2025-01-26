import grpc
import ai911dispatcher_pb2
import ai911dispatcher_pb2_grpc

# Function to test InitiateSession
def test_initiate_session(stub):
    user = ai911dispatcher_pb2.User(phoneNum="555-1234")
    response = stub.InitiateSession(user)
    print(f"InitiateSession Response: {response.status}")

# Function to test SendCallerResponse
def test_send_caller_response(stub):
    caller_response = ai911dispatcher_pb2.CallerResponse(Response="My name is robert smith, my phone number is 713-888-0012, I am located on the intersection of texas and university, and their is a fire raging at the intersection")
    response = stub.SendCallerResponse(caller_response)
    print(f"SendCallerResponse Response: {response.status}")

# Function to test SendCallerResponse
def test_send_caller_response2(stub):
    caller_response = ai911dispatcher_pb2.CallerResponse(Response="My name is robert smith, I am located on the intersection of texas and university, and their is a fire raging at the intersection, my cat is stuck in my chimmey toO!")
    response = stub.SendCallerResponse(caller_response)
    print(f"SendCallerResponse Response: {response.status}")


# Function to test EndSession
def test_end_session(stub):
    user = ai911dispatcher_pb2.User(phoneNum="555-1234")
    response = stub.EndSession(user)
    print(f"EndSession Response: {response.status}")

# Main function to create a gRPC channel and stub
def run():
    # Connect to the gRPC server (assumes the server is running on localhost:50051)
    channel = grpc.insecure_channel('localhost:50051')
    stub = ai911dispatcher_pb2_grpc.MainServiceStub(channel)

    # Test the gRPC methods
    #test_initiate_session(stub)
    #test_send_caller_response(stub)
    test_send_caller_response2(stub)

    #test_end_session(stub)

if __name__ == '__main__':
    run()
