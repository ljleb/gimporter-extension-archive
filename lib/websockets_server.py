import websockets
import asyncio
import threading
import queue


websocket_server_address = ('localhost', 7862)
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


async def start_server_async(local_elem_ids_queue):
    async with websockets.serve(accept_connection, *websocket_server_address):
        await server_main(local_elem_ids_queue)


def start_server_sync(local_elem_ids_queue):
    server_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(server_loop)
    asyncio.run(start_server_async(local_elem_ids_queue))


elem_ids_queue = queue.Queue()
_server_thread = threading.Thread(target=start_server_sync, args=(elem_ids_queue,), daemon=True)


def start_server():
    if not _server_thread.ident:
        _server_thread.start()
        print(f'[gimporter] websocket server started on {websocket_server_address[0]}:{websocket_server_address[1]}')
