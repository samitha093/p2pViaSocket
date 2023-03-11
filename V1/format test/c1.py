import socket
import time

try:
    # connect to server socket
    server_ip = '13.250.112.193'
    server_port = 9000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    message = ''
    client_socket.sendall(message.encode())
    response = client_socket.recv(1024).decode()
    print("Server arranged Socket: ", response)
    client_socket.close()

    # connect to temp socket
    Tsocket = int(response)
    com_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    com_socket.connect((server_ip, Tsocket))
    datamodel = "test stream from model"
    com_socket.sendall(datamodel.encode())

    # while True:
    #     time.sleep(5)
    #     data = com_socket.recv(1024).decode()
    #     print("Server Data response:", data)

    com_socket.close()

except Exception as e:
    print(f"Error: {e}")