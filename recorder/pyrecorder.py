import wave
import struct
import os
import grpc
import ai911dispatcher_pb2_grpc
import ai911dispatcher_pb2
import ai911displaychatdisplay_pb2
import ai911displaychatdisplay_pb2_grpc
from openai import OpenAI
from dotenv import load_dotenv
from pvrecorder import PvRecorder
import keyboard

# Load environment variables from .env file
load_dotenv()

# Fetch the OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OpenAI API key not found. Ensure it is set in the .env file.")

# Initialize the OpenAI client
client = OpenAI(api_key=openai_api_key)

# Initialize the recorder
recorder = PvRecorder(device_index=-1, frame_length=512)

# Function to save the audio chunk to a WAV file
def save_audio(audio_chunk, samplerate, filename):
    # Scale audio to fit 16-bit range
    audio_chunk = [max(min(x, 32767), -32768) for x in audio_chunk]

    # Save audio to a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 16-bit samples
        wf.setframerate(samplerate)
        wf.writeframes(struct.pack("h" * len(audio_chunk), *audio_chunk))

    print("Audio successfully saved")

# Function to transcribe audio using OpenAI's Whisper API
def transcribe_audio(audio_filename):
    # Transcribe the audio
    response = None
    with open(audio_filename, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        # Create the CallerResponse message with the transcript
        response = ai911dispatcher_pb2.CallerResponse(Response=transcription.text)
        display_msg = ai911displaychatdisplay_pb2.PublishMessageRequest(role="User",contents=transcription.text,time="latest")
    # Send the message to the server
    try:
        success = stub.SendCallerResponse(response)
        display_success = display_stub.PublishMessage(display_msg)
        print(f"Server response: {success.status}")
    except grpc.RpcError as e:
        print(f"Error sending response: {e.details()}")

    # Print transcription
    print(f"Transcription: {transcription}")

# Record the audio from microphone input
def record_audio():
    audio = []
    transcription = ""
    audio_filename = "audio_output.wav"
    
    # Start recording
    try:
        print("Press 'q' to stop recording.")
        recorder.start()
        
        while True:
            frame = recorder.read()
            audio.extend(frame)

            # Check for keypress to stop recording
            if keyboard.is_pressed('q'):  # Stop recording when 'q' is pressed
                print("Key 'q' pressed. Stopping recording.")
                break

        # Save the recorded audio to a WAV file
        print(f"Saving audio to: {audio_filename}")
        save_audio(audio, 16000, audio_filename)

        # Transcribe audio
        transcribe_audio(audio_filename)

        # Clean up the audio file by deleting it
        os.remove(audio_filename)
    
    finally:
        recorder.stop()
        recorder.delete()

# Main function to handle user choice
def main():
    # Prompt user to enter input choice
    print("Choose an option:")
    print("1. Record a new audio file")
    print("2. Transcribe an existing audio file")
    choice = input("Enter your choice (1/2): ").strip()

    # Redirect as necessary
    if choice == "1":
        record_audio()
    elif choice == "2":
        file_path = input("Enter the path to the audio file: ").strip()
        if os.path.exists(file_path):
            transcribe_audio(file_path)
        else:
            print(f"File not found: {file_path}")
    else:
        print("Invalid choice. Please enter 1 or 2.")

channel = grpc.insecure_channel('10.242.149.215:50051')
stub = ai911dispatcher_pb2_grpc.MainServiceStub(channel)

display_channel = grpc.insecure_channel('10.242.23.76:50051')
display_stub = ai911displaychatdisplay_pb2_grpc.Ai911DispatcherChatDisplayStub(display_channel)

# Run the main function
main()