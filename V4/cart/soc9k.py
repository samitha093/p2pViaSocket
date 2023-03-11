import socket
import struct
import threading
import pickle
import time
import sys
from filesender import partDevider


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
        self.socketFree = True

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
        continueData = False
        while self.is_running:
            try:
                data_chunks = []
                while True:
                    try:
                        self.socket.settimeout(3)
                        received_data = self.socket.recv(1024*1024)
                        print("Data receiving .....")
                        continueData = True
                    except socket.timeout:
                        if continueData:
                            print("Data received done.")
                            continueData = False
                        break
                    except:
                        break
                    data_chunks.append(received_data)
                if len(data_chunks) == 0:
                    continue
                print("Data Processing Started.")
                data = b''.join(data_chunks)
                decordedData = pickle.loads(data)
                print("RECIVED DATA FROM : ",decordedData.get("Sender"))
                self.RECIVEQUE.append(decordedData)
            except:
                continue

    def start_sender(self):
        self.is_running = True
        self.sender_thread = threading.Thread(target=self.sender)
        self.sender_thread.start()

    def sender(self):
        while self.is_running:
            if(len(self.SENDQUE) > 0):
                toDumpData = self.SENDQUE[0].copy()
                data = pickle.dumps(toDumpData)
                self.SENDQUE.remove(self.SENDQUE[0])
                data_size = sys.getsizeof(data)
                data_size_kb = data_size / 1024
                if data_size_kb < 30:
                    self.socket.sendall(data)
                elif data_size_kb < 7000:
                    print("OVERLOADED DATAPACK FOUND : ",data_size_kb, "KB")
                    partDevider(self.socket, data)
                else:
                    print("OVERLOADED DATAPACK FOUND : ",data_size_kb, "KB")
                    print("Cant Send more than 5MB data file ")
                time.sleep(2)

    def request(self, data):
        self.SENDQUE.append(data)

    def queueClean(self,data):
        self.RECIVEQUE.remove(data)

    def close(self):
            self.is_running = False
            print("Socket connections are being disrupted.")
            self.socket.close()
