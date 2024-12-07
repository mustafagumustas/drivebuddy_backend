import asyncio
import websockets
import openai
import dotenv
import os

# Configure OpenAI API key
from openai import AsyncOpenAI

load_status = dotenv.load_dotenv("accounts/variables.txt")
client = AsyncOpenAI()
# Host and port for WebSocket server
HOST = "0.0.0.0"  # Accessible from all IPs
PORT = 8080


async def handle_audio_stream(websocket):
    try:
        # Receive text from the WebSocket client
        input_text = await websocket.recv()
        print(f"Received text: {input_text}")

        # Use OpenAI's TTS API to stream audio to the file
        async with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice="alloy", input=input_text, response_format="pcm"
        ) as response:
            await response.stream_to_file("output.pcm")

        # Read the file in chunks and send via WebSocket
        with open("output.pcm", "rb") as audio_file:
            while chunk := audio_file.read(1024):  # Adjust chunk size as needed
                await websocket.send(chunk)
                print(f"Sent chunk of size {len(chunk)} bytes")

        print("Audio stream sent successfully")

        # Clean up the temporary file
        os.remove("output.pcm")

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        print("Client disconnected")


async def main():
    server = await websockets.serve(handle_audio_stream, HOST, PORT)
    print(f"WebSocket server started on ws://{HOST}:{PORT}")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
