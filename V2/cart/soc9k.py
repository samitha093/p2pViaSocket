import socket
import threading
import json
import time
import sys

class peerCom:
    def __init__(self, host, port, timerout):
        self.host = host
        self.port = port
        self.timerout = timerout
        self.socket = None
        self.receiver_thread = None
        self.is_running = False
        self.SENDQUE = []
        self.RECIVEQUE = []

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        data = self.socket.recv(1024)
        USERID = repr(data.decode('utf-8'))[1:-1]
        return USERID

    def start_receiver(self):
        self.is_running = True
        self.receiver_thread = threading.Thread(target=self.receiver)
        self.receiver_thread.start()

    def receiver(self):
        while self.is_running:
            try:
                data = self.socket.recv(5 * 1024 * 1024)
                decordedData = json.loads(data.decode("utf-8"))
                self.RECIVEQUE.append(decordedData)
                time.sleep(0.1)
            except:
                continue

    def start_sender(self):
        self.is_running = True
        self.sender_thread = threading.Thread(target=self.sender)
        self.sender_thread.start()

    def sender(self):
        while self.is_running:
            if(len(self.SENDQUE) > 0):
                data = json.dumps(self.SENDQUE[0])
                self.SENDQUE.remove(self.SENDQUE[0])
                data_size = sys.getsizeof(data)
                data_size_kb = data_size / 1024
                if data_size_kb < 1:
                    self.socket.sendall(data.encode())
                    time.sleep(0.1)
                else:
                    print("OVERLOADED DATAPACK FOUND: ",data_size_kb, "KB")

    def request(self, data):
        self.SENDQUE.append(data)

    def queueClean(self,data):
        self.RECIVEQUE.remove(data)

    def close(self):
        self.is_running = False
        print("Socket connections are being disrupted.")
        self.socket.close()