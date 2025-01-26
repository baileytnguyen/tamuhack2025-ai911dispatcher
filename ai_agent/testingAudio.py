from pathlib import Path
from dotenv import load_dotenv#load dot ENV
import os
from openai import OpenAI
import winsound


openai_api_key = os.getenv("OPENAI_API_KEY")

def tts(speach):
    # Load environment variables from .env file

    client = OpenAI()
    speech_file_path = Path(__file__).parent / "speech.wav"
    response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=speach,
    )
    response.stream_to_file(speech_file_path)


#ts("I love texas a&m gig em ags")
winsound.PlaySound("speech.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
