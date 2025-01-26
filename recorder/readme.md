# AI 911 Dispatcher Audio Processing Script

This project processes and transcribes audio using OpenAI's Whisper API and gRPC communication to interact with a remote AI-based 911 dispatcher service. It supports live audio recording and transcription of pre-existing audio files.

## Features

- **Live Audio Recording**: Record audio in real-time from your microphone.
- **Audio Transcription**: Use OpenAI's Whisper API to transcribe recorded or existing audio files.
- **gRPC Communication**: Sends transcription data to a remote AI 911 dispatcher service for further processing.
- **User-Friendly Controls**: Start recording or transcribing via simple keyboard inputs.

## Prerequisites

- Python 3.8 or higher
- A valid OpenAI API key
- The following Python libraries:
  - `wave`
  - `struct`
  - `os`
  - `grpc`
  - `whisper`
  - `pvrecorder`
  - `keyboard`

## Installation

1. **Clone the Repository**
    git clone https://github.com/baileytnguyen/tamuhack2025-ai911dispatcher
    cd ai-911-dispatcher

2. **Set Up a Virtual Environment:**
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate

3. **Install Dependencies:**
    pip install -r requirements.txt

4. **Configure OpenAI API Key:**
    Replace the placeholder openai_api_key in the script with your OpenAI API key.

5. **Set Up gRPC:**
    Ensure your gRPC server is running and reachable. Replace the channel address (10.242.149.215:50051) in the script with the actual address of your gRPC server.

## Usage

1. **Run the Script:**
    python pyrecorder.py

2. **Choose an Option:**
    Record a new audio file for transcription.
    OR
    Transcribe an existing audio file.

3. **Controls for Recording:**
    Press q to stop recording.

## File Structure

- **ai911dispatcher_pb2.py and ai911dispatcher_pb2_grpc.py:**
    Auto-generated gRPC files for communication with the remote server.
- **pyrecorder.py:**
    The main script for recording, saving, transcribing, and interacting with the gRPC service.

## Key Functions

- **load_whisper_model:** Loads the Whisper transcription model.
- **save_audio:** Saves audio input as a WAV file.
- **transcribe_audio:** Transcribes audio using Whisper and sends the results to the gRPC server.
- **record_audio:** Records audio from the microphone and triggers transcription.
- **main:** Handles user interaction and options.

## Dependencies

Install the following libraries via pip if not already included in the requirements file:
    
    pip install wave struct grpc whisper openai pvrecorder keyboard

## Notes

- Ensure your microphone and audio input devices are configured properly.
- Audio files are deleted automatically after processing to maintain a clean workspace.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- OpenAI Whisper
- gRPC Python
- PvRecorder