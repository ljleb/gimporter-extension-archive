import socket
import threading
from PIL import Image


class SocketAttr:
    def __init__(self, connection, client_address):
        self.connection = connection
        self.client_address = client_address


gimp_server_address = ('localhost', 7861)
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(gimp_server_address)
serv.listen(1)
print(f'[gimporter] socket server started on {gimp_server_address[0]}:{gimp_server_address[1]}')
server_thread = None
recv_callback = None


def set_recv_callback(callback):
    global recv_callback
    recv_callback = callback


def start_server():
    global server_thread

    def accept_gimp_connection_and_block_read():
        while True:
            gimp_socket = SocketAttr(*serv.accept())
            receive_data_from_gimp_blocking(gimp_socket)

    if server_thread is None:
        server_thread = threading.Thread(target=accept_gimp_connection_and_block_read, daemon=True)
        server_thread.start()


def receive_data_from_gimp_blocking(gimp_socket):
    global recv_callback
    data = read_data_blocking(gimp_socket)
    parsed = parse_images_from_socket_data(data)
    if recv_callback is not None:
        recv_callback(*parsed)


def read_data_blocking(gimp_socket):
    amount_to_read = gimp_socket.connection.recv(4)
    amount_to_read = int.from_bytes(amount_to_read, 'big')
    data = bytearray()
    amount_received = 0
    while amount_received < amount_to_read:
        received_packet = gimp_socket.connection.recv(amount_to_read)
        amount_received += len(received_packet)
        if amount_received == 0:  # connection died
            break
        data.extend(received_packet)
    return bytes(data)


def parse_images_from_socket_data(data):
    tab = data[0:7].decode("utf-8")
    data = data[7:]
    image, offset = parse_image_packet(data)
    if tab != 'inpain2':
        return tab, image, None,
    data = data[offset:]
    mask, _ = parse_image_packet(data)
    return 'inpaint', image, mask,


def parse_image_packet(data):
    width = int.from_bytes(data[:4], 'big')
    height = int.from_bytes(data[4:8], 'big')
    bpp = int.from_bytes(data[8:12], 'big')
    image_size = int.from_bytes(data[12:16], 'big')
    image_dim = (width, height)
    image_mode_bpp_map = [None, 'L', None, 'RGB', 'RGBA']
    image_mode = image_mode_bpp_map[bpp]
    image_data = data[16:16+image_size]
    image = Image.frombytes(image_mode, image_dim, image_data)
    return image, 16+image_size
