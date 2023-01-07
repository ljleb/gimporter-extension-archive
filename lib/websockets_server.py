import websockets
import asyncio
import threading
import queue


_connected_clients = set()


async def accept_connection(websocket):
    _connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        _connected_clients.remove(websocket)


async def server_main(local_elem_ids_queue):
    while True:
        elem_ids = await asyncio.to_thread(local_elem_ids_queue.get)
        for elem_id in elem_ids:
            websockets.broadcast(_connected_clients, elem_id)


server_loop = asyncio.new_event_loop()


async def start_server_async(local_elem_ids_queue):
    async with websockets.serve(accept_connection, "localhost", 7861):
        await server_main(local_elem_ids_queue)


def start_server_sync(local_elem_ids_queue):
    asyncio.set_event_loop(server_loop)
    asyncio.run(start_server_async(local_elem_ids_queue))


elem_ids_queue = queue.Queue()
_server_thread = threading.Thread(target=start_server_sync, args=(elem_ids_queue,), daemon=True)


def start_server():
    _server_thread.start()
