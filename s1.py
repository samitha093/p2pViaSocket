import asyncio
import random
import socket
import time

class pvtSocket:
    def __init__(self, portNo):
        self.Tserver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = portNo

    async def connect(self):
        self.Tserver_socket.bind(('', self.port))
        self.Tserver_socket.listen()
        print("Private socket start/listening on port", self.port)
        while True:
            conn, addr = await loop.sock_accept(self.Tserver_socket)
            asyncio.create_task(handle_temp_client(conn, addr, self.port))

    def __str__(self):
        return "true"


async def handle_temp_client(conn, addr, port):
    print("Private Socket : ",port," => Client connected : ", addr)
    await asyncio.sleep(1)
    datset = 'test sender'
    conn.sendall(str(datset).encode())
    time.sleep(5)
    datset2 = 'test sender 2'
    conn.sendall(str(datset2).encode())
    time.sleep(10)
    datset3 = 'test sender 3'
    conn.sendall(str(datset3).encode())


async def handle_client(client_socket, client_address):
    print("Received message from client", client_address)
    port = random.randint(10000, 65535)
    tempclient = pvtSocket(port)
    asyncio.create_task(tempclient.connect())
    newport = str(port)
    await loop.run_in_executor(None, client_socket.sendall, newport.encode())
    client_socket.close()


async def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 8080
    server_socket.bind(('', port))
    server_socket.listen()
    print("Server listening on port", port)

    while True:
        client_socket, client_address = await loop.sock_accept(server_socket)
        asyncio.create_task(handle_client(client_socket, client_address))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
