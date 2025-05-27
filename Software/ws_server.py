import asyncio
import websockets
import threading

clients = set()

async def broadcast(message):
    for client in clients:
        try:
            await client.send(message)
        except:
            pass

async def handler(websocket):
    clients.add(websocket)
    try:
        async for _ in websocket:
            pass
    finally:
        clients.remove(websocket)

def start_websocket_server():
    async def main():
        async with websockets.serve(handler, "0.0.0.0", 8765):
            await asyncio.Future()
        
    threading.Thread(target=lambda: asyncio.run(main()), daemon=True).start()

def send_log(message):
    asyncio.run(broadcast(message))