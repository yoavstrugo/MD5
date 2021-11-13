import socket
from math import floor, ceil
from threading import Thread
from protocol import send, receive

ADDR = ('localhost', 8888)
NUM_OF_CLIENTS = 10


class MD5Server:
    def __init__(self, addr):
        self._clients: list[tuple[socket, int]] = []
        self._socket: socket = socket.socket()
        self._addr: tuple[str, int] = addr
        self._accepting_clients: bool = False
        self._cores = 0
        self._run = True

    def _accept_clients(self):
        while self._accepting_clients:
            client, addr = self._socket.accept()

            self._get_cores(client)

            if len(self._clients) >= NUM_OF_CLIENTS:
                self._accepting_clients = False

    def _get_cores(self, client: socket):
        msg = {'method': 'cores'}
        send(client, msg)
        reply: dict = receive(client)
        cores = reply['cores']
        self._clients.append((client, cores))
        self._cores += cores

        print(f'Client has connected with {cores} cores!')

    def _listener(self, client: tuple[socket, int]):
        while self._run:
            msg = receive(client[0])
            if msg['method'] == 'found':
                print('Client has found the correct number!')
                print(msg['num'])
                self.stop()
            elif msg['method'] == 'done':
                print('A client has finished his range.')
                self._clients.remove(client)
                break

    def divide_task(self, num_range, hash_length, hash_output):
        print(f'Reached {NUM_OF_CLIENTS} clients, starting dividing.')

        per_core = num_range / self._cores

        divided_cores = 0
        for client in self._clients:
            # Calculate the range
            start_num = floor(divided_cores * per_core)
            end_num = ceil((divided_cores + client[1]) * per_core - 1)
            divided_cores += client[1]

            client_info = {'method': 'look_for_hash', 'start': start_num, 'end': end_num, 'hash_length': hash_length,
                           'hash_output': hash_output}

            send(client[0], client_info)

            listener_thread = Thread(target=self._listener, args=(client,))
            listener_thread.start()

    def broadcast(self, msg: dict):
        for client in self._clients:
            send(client[0], msg)

    def stop(self):
        self.broadcast({'method': 'stop'})
        self._run = False
        self._socket.close()

    def start(self):
        # Start listening for clients
        self._socket.bind(ADDR)
        self._socket.listen()

        # Accept clients
        self._accepting_clients = True
        self._accept_clients()


if __name__ == '__main__':
    server = MD5Server(ADDR)
    server.start()
    server.divide_task(9999999999, 10, 'EC9C0F7EDCC18A98B1F31853B1813301')

# Number is: 3735928559