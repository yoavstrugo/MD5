import random
import socket
import json


def send(sock: socket, msg: dict):
    # Calc the size of the message and create the packet
    msg_str = json.dumps(msg)
    msg_len = len(msg_str)
    packet_str = f'{msg_len};' + msg_str

    try:
        sock.sendall(packet_str.encode('utf-8'))  # send it
    except OSError:
        pass  # Socket has disconnected


def receive(sock: socket) -> dict:
    buffer = ''
    # first we need to get the length of the message
    # The length of the message is separated by semicolon, read until 
    # we reach one
    while ';' not in buffer:
        try:
            buffer += sock.recv(1).decode('utf-8')
        except OSError:
            pass  # Socket has disconnected

    # This should be the length of the msg
    msg_len = int(buffer[:-1])

    # Reset the buffer once again
    buffer = ''

    # keep reading until we read the whole message
    while len(buffer) < msg_len:
        try:
            buffer += sock.recv(1).decode('utf-8')
        except OSError:
            pass  # Socket has disconnected

    # We finished reading
    return json.loads(buffer)
