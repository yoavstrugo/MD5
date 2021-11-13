import socket
import os
import sys
from math import floor, ceil
from hashlib import md5

from protocol import send, receive
from threading import Thread


class MD5Client:
    def __init__(self, addr):
        self._sock = socket.socket()
        self._addr = addr
        self._run = True
        self._cores = os.cpu_count()
        self._remaining_cores = self._cores

    def _search(self, start_num: int, end_num: int, hash_length: int, hash_output: str):
        for i in range(start_num, end_num + 1):
            if not self._run:
                break

            md5_input = str(i).zfill(hash_length)
            if md5(md5_input.encode()).hexdigest().upper() == hash_output.upper():
                send(self._sock, {'method': 'found', 'num': md5_input})
                print('I found')

        self._remaining_cores -= 1
        if self._remaining_cores == 0:
            send(self._sock, {'method': 'done'})
            print('I finished')
            self.stop()

    def _hash_search_manager(self, start_num: int, end_num: int, hash_length: int, hash_output: str):
        per_core = (end_num - start_num) / self._cores  # how many numbers per core
        for i in range(self._cores):
            if not self._run:
                break

            core_start = floor(i * per_core + start_num)
            core_end = ceil((i + 1) * per_core + start_num)

            search_thread = Thread(target=self._search, args=(core_start, core_end, hash_length, hash_output))
            search_thread.start()

    def _listener(self):
        while self._run:
            msg = receive(self._sock)
            if msg['method'] == 'cores':
                print('Server asked for cores')
                send(self._sock, {'cores': self._cores})
            elif msg['method'] == 'look_for_hash':
                print('Server asked to start looking for the hash')
                hash_search_thread = Thread(target=self._hash_search_manager,
                                            args=(msg['start'], msg['end'], msg['hash_length'], msg['hash_output']))
                hash_search_thread.start()
            elif msg['method'] == 'stop':
                print('Server asked to stop')
                self.stop()

    def stop(self):
        self._sock.close()
        self._run = False
        sys.exit()

    def start(self):
        # Connect
        self._sock.connect(self._addr)

        # Start listening
        listener_thread = Thread(target=self._listener)
        listener_thread.start()


if __name__ == '__main__':
    client = MD5Client(('localhost', 8888))
    client.start()
