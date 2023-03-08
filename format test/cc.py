import socket

host = '13.250.112.193'
port = 8080
timeout = 5  # in seconds

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(timeout)

try:
    sock.connect((host, port))
    print(f"Port {port} on {host} is open")
except socket.error:
    print(f"Port {port} on {host} is closed")

sock.close()
