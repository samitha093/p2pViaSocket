import asyncio
import random
import time

HOST = ''
PORT = 9000

# This is the coroutine that will handle incoming client connections
async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print('----------------------------------------------------------------')
    print('Connected by', addr)  # print a message when a client connects
    while True:
        data = await reader.read(1024)  # read up to 1024 bytes of data from the client
        if not data:
            break  # if no data was received, exit the loop
    writer.close()  # close the connection to the client

# This is the main coroutine that starts the server
async def main():
    # start the server and bind it to the specified host and port
    server = await asyncio.start_server(handle_client, HOST, PORT)
    # print a message to indicate that the server is running
    print("Server listening on port", PORT)

    async with server:
        # start serving incoming connections forever
        await server.serve_forever()

# The following code runs the main coroutine as an asyncio task
if __name__ == "__main__":
    asyncio.run(main())
