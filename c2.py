import socket
import time
import threading

SOCKETTIMER = 12 ## 12 => 60s
HOST = 'localhost'
# HOST = '13.250.112.193'
PORT = 9000
QUEUE =[]
SENDERSTOCK =[]
RECEVERSTOCK =[]
USERID = ""
CLUSTERID = ""
CLUSTERLIST= []
QUEUE_LOCK = threading.Lock()
USERID_LOCK = threading.Lock()
CLUSTERID_LOCK = threading.Lock()
CLUSTERLIST_LOCK = threading.Lock()

#request Cluster ID
def ReqCluserId(UserId):
    global QUEUE
    requst = ["CLUSTER",UserId,"PENDING"]
    with QUEUE_LOCK:
        QUEUE.append(requst)

#request user's peer list from cluster
def ReqPeerList(clusterId):
    global QUEUE
    requst = ["PEERLIST",clusterId,"PENDING"]
    with QUEUE_LOCK:
        QUEUE.append(requst)

#request a model parameters from another peer in same cluster
def ReqModel(peerId,clusterId,UserId):
    return ["REQUESTMODEL",[peerId,clusterId,UserId],"PENDING"]

#Send model parameters when found request
def SendModel(parameters,peerId):
    print('Start Request model to : ', peerId)

#response handler
def ResHandler(self,response):
    global CLUSTERID
    global CLUSTERLIST
    global SENDERSTOCK
    if self == "CLUSTERID":
        with CLUSTERID_LOCK:
            CLUSTERID = response
        print("CLUSTER ID : ",response)
    if self == "PEERLIST":
        with CLUSTERLIST_LOCK:
            CLUSTERLIST = response
        print("PEER LIST:",CLUSTERLIST)
    if self == "REQUESTMODEL":
        SENDERSTOCK.append(["SENDMODEL",["this is the data","Format"],response[1][0],response[1][2]])
        print("RECIEVED : ",response)
    if self == "SENDMODEL":
        QUEUE.pop(0) #should validate wht i recived and from where
        print("RECIEVED MODEL : ",response)
    return

#function to handle socket connection
def socket_handler():
    global USERID
    global QUEUE
    global SOCKETTIMER
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    waitTime = 0
    selfClose = 0
    ##############################USER_ID###################################
    with USERID_LOCK:
        data = s.recv(1024)
        USERID = repr(data.decode('utf-8'))[1:-1]
        print('USER ID : ',USERID )
    ##############################SOCKET_HANDLER############################
    while True:
        #FulFill Request DataModel
        if len(SENDERSTOCK) > 0:
            s.sendall(str(SENDERSTOCK[0]).encode())
            del SENDERSTOCK[0]
        # send request to socket
        if len(QUEUE) != 0:
            selfClose = 0
            if QUEUE[0][-1] == "PENDING":
                time.sleep(waitTime)
                print("REQUEST : ",QUEUE[0])
                QUEUE[0][-1] = "REQUESTED"
                s.sendall(str(QUEUE[0]).encode())
                # data = s.recv(1024)
                # print(repr(data.decode('utf-8')))
        else:
            if selfClose >= SOCKETTIMER:
                break
            selfClose += 1
        #listning for socket connection
        try:
            #Timeout of 5 seconds
            s.settimeout(5)
            data = repr(s.recv(51200).decode('utf-8'))[1:-1]  # maximum reciver 50MB
            print(data)
            try:
                response = eval(data)
            except TypeError as e:
                print("Have an error on recived data:", e)
            if response[0] == 0: #error handler
                waitTime += 5
                QUEUE[0][-1] = "PENDING"
                print('RESPONSE : ', response[1])
            elif response[0] == 1: #Ack
                print(response[1])
            else: #responce
                waitTime = 0
                if (QUEUE[0][-1] =="REQUESTED") & ((QUEUE[0][0] == "CLUSTER")|(QUEUE[0][0] == "PEERLIST")):
                    del QUEUE[0]
                response_thread = threading.Thread(target=ResHandler, args=response)
                response_thread.start()
        except socket.timeout:
            continue
    ########################################################################
    s.close() ##### manually close the socket connection

#start the socket thread
socket_thread = threading.Thread(target=socket_handler)
socket_thread.start()
################################################################
#main thread continues to execute
################################################################
while True: #-------------------------Request cluster id
    with USERID_LOCK:
        if USERID != "":
            ReqCluserId(USERID)
            break
while True: #-------------------------Request Cluster list
    with CLUSTERID_LOCK:
        if CLUSTERID != "":
            ReqPeerList(CLUSTERID)
            break
while True: #-------------------------Request Model paramers
    with CLUSTERLIST_LOCK:
        if len(CLUSTERLIST) >0:
            TempArray = []
            for PEERID in CLUSTERLIST:
                if PEERID != USERID:
                    request = ReqModel(PEERID,CLUSTERID,USERID)
                    TempArray.append(request)
            QUEUE += TempArray
            print("***********",QUEUE)
            break
################################################################
