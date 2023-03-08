import asyncio
import random
import socket

async def handle_client(client_socket, client_address):
    print("Received message from client", client_address)
    port = random.randint(10000, 65535)
    #create pvt socket
    await loop.run_in_executor(None, client_socket.sendall, str(port).encode())
    client_socket.close()


async def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 9000
    server_socket.bind(('', port))
    server_socket.listen()
    print("Server listening on port", port)

    while True:
        client_socket, client_address = await loop.sock_accept(server_socket)
        asyncio.create_task(handle_client(client_socket, client_address))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())