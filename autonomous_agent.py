import ggwave
import pyaudio
import time
import os
from google import genai

# Setup Gemini (using the environment variable for API Key)
# Make sure to set GOOGLE_API_KEY in your env
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# GGWave setup
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=48000, input=True, frames_per_buffer=1024)
stream_out = p.open(format=pyaudio.paInt16, channels=1, rate=48000, output=True)
instance = ggwave.init()

print('Autonomous AI Agent Active: Listening ...')

def transmit(text):
    print(f"Transmitting: {text}")
    waveform = ggwave.encode(text, 1, 10, instance)
    stream_out.write(waveform)
    print(f"Sent {len(waveform)} bytes of audio.")

try:
    while True:
        data = stream.read(1024, exception_on_overflow=False)
        res = ggwave.decode(instance, data)
        if res is not None:
            text = res.decode("utf-8")
            print(f"Heard: {text}")
            
            # The "Brain" part
            response = client.models.generate_content(
                model='models/gemini-2.5-flash-lite',
                contents=f"You are an autonomous audio agent. Reply briefly to this message: {text}"
            )
            transmit(response.text)

except KeyboardInterrupt:
    print("Stopping...")

ggwave.free(instance)
stream.stop_stream()
stream.close()
stream_out.stop_stream()
stream_out.close()
p.terminate()
