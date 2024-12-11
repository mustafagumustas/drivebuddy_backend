import asyncio
import websockets
import dotenv
from openai import AsyncOpenAI
import os

# Configure OpenAI API key
load_status = dotenv.load_dotenv("accounts/variables.txt")
client = AsyncOpenAI()

# Host and port for WebSocket server
HOST = "0.0.0.0"  # Accessible from all IPs
PORT = 8080


async def handle_audio_stream(websocket):
    try:
        input_text = await websocket.recv()
        print(f"Received text: {input_text}")

        # Get AAC data from OpenAI
        async with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=input_text,
            response_format="aac",
        ) as response:
            # Stream directly to websocket in controlled chunk sizes
            buffer = bytearray()
            async for chunk in response.iter_bytes():
                buffer.extend(chunk)
                while len(buffer) >= 1024:  # Control chunk size to 1024 bytes
                    await websocket.send(buffer[:1024])
                    print(f"Sent chunk of size: 1024 bytes")
                    buffer = buffer[1024:]

            # Send any remaining data in the buffer
            if buffer:
                await websocket.send(buffer)
                print(f"Sent final chunk of size: {len(buffer)} bytes")

        # Send an "END" message to indicate streaming is complete
        await websocket.send("STREAM_COMPLETE")
        print("Audio stream completed, waiting for client to close...")

        # Wait for client's close signal
        try:
            close_signal = await websocket.recv()
            print(f"Received close signal from client: {close_signal}")
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected without sending close signal")

    except Exception as e:
        print(f"Error in handle_audio_stream: {str(e)}")
        raise
    finally:
        print("Connection closed")


async def main():
    server = await websockets.serve(handle_audio_stream, HOST, PORT)
    print(f"WebSocket server started on ws://{HOST}:{PORT}")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
