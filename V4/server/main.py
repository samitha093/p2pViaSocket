import asyncio
import pickle
import struct
import sys
from rndGen import generateId

HOST = ''  # The server's hostname or IP address
PORT = 9000        # The port used by the server

DeviceTable = []
ClusterTable = {}
clusterSize = 2

DATARECORDER = {}

def responceModel(msgTo, data, msgFrom="SERVER"):
    return {
        'Sender':msgFrom,
        'Receiver': msgTo,
        'Data':data
    }

def reqirementHandler(data):
    global DATARECORDER
    #############################################################
    ##Clustering Process Start        ---------------------------
    User = data.get("Sender")
    req = data.get("Data")
    if req[0] == "PEERTYPE":
        DeviceTable.append(User)
        if len(DeviceTable) >= clusterSize:
            temptable  = DeviceTable.copy()
            DeviceTable.clear()
            ClusterId = generateId(12)
            ClusterTable[ClusterId] = temptable.copy()
            print("Custer created : ",ClusterId," : ",ClusterTable.get(ClusterId))
        ##Clustering Process END          ---------------------------
            defineCluster = ["CLUSTERID",ClusterId, "PEERLIST",ClusterTable.get(ClusterId)]
            for X in temptable:
                tempData = responceModel(X,defineCluster)
                mailBox = DATARECORDER.get(X)
                mailBox.append(tempData)

def requestHandler(data):
    User = data.get("Receiver")
    req = data.get("Data")
    if req[0] == "MODELREQUEST":
        mailBox = DATARECORDER.get(User)
        mailBox.append(data)
    if req[0] == "MODELPARAMETERS":
        mailBox = DATARECORDER.get(User)
        mailBox.append(data)

# This is the coroutine that will handle incoming client connections
async def handle_client(reader, writer):
    print('----------------------------------------------------------------')
    addr = writer.get_extra_info('peername')
    print('Connected by', addr)
    ##################USER_ID####################################
    userId = generateId(16)
    DATARECORDER[userId] = []
    print('User id : ', userId)
    writer.write(userId.encode())
    await writer.drain()
    ######################RUNNER_ENGINE##########################
    while True:
        #Sender handler -----------------------------------------
        if len(DATARECORDER.get(userId)) > 0:
            mailBox = DATARECORDER.get(userId)
            if mailBox[0].get("Data")[0] == "MODELPARAMETERS":
                    print("****MODELPARAMETERS FROM ",mailBox[0].get("Sender")," TO : ", userId)
            mailData = pickle.dumps(mailBox[0])
            data_size = sys.getsizeof(data)
            data_size_kb = data_size / 1024
            if data_size_kb < 1:
                writer.write(mailData)
                await writer.drain()
            else:
                print("OVERLOADED DATA FOUND : ",data_size_kb,"KB")
                MAX_CHUNK_SIZE = 1024
                chunks = [mailData[i:i+MAX_CHUNK_SIZE] for i in range(0, len(mailData), MAX_CHUNK_SIZE)]
                print("NO OF CHUNKS : ",len(chunks)," : SENDED")
                for x in chunks:
                    writer.write(x)
                    await writer.drain()
            mailBox.remove(mailBox[0])
        #Reciver handler-----------------------------------------
        try:
            # Receive and concatenate the data chunks
            data_chunks = []
            while True:
                try:
                    data = await asyncio.wait_for(reader.read(1024*1024), timeout=1)
                except asyncio.TimeoutError:
                    break
                data_chunks.append(data)
            # Concatenate the chunks into a single bytes object
            if len(data_chunks) == 0:
                continue
            data = b''.join(data_chunks)
            decordedData = pickle.loads(data)
        except Exception as e:
            print("######## STATUS INFO : ",e)
            break
        if decordedData.get("Receiver") == "SERVER":
            reqirementHandler(decordedData)
        else:
            requestHandler(decordedData)
    #############################################################
    writer.close()
    print('Connection Closed : ',addr)

# This is the main route that starts the server on here
async def main():
    # start the server and bind it to the specified host and port
    server = await asyncio.start_server(handle_client, HOST, PORT)
    # print a message to indicate that the server is running
    print("Server listening on port", PORT)

    async with server:
        # start serving incoming connections forever
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())