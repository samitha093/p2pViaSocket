import asyncio
import random
import string
import time
import threading

clusterSize = 3 #### cluster size
HOST = ''
PORT = 9000   ####Reciving port for carts
existing_ids = []

DeviceTable = {}
ClusterTable = {}
TaskQUEUE = {}
TASKHOLDER = []

#Command management for give response
def CommanManager(resquest, user):
    print(user," : Request : ",resquest)
    result =[0,"Can't identify command"]
    decoded_data = resquest.decode("utf-8")
    extracted_data = decoded_data.strip("[]").split(", ")
    commandQ = extracted_data[0]
    command = commandQ[1:-1]
    if str(command.strip().upper()) == "CLUSTER":
        print("Command Found : ",command)
        UserIdNo = extracted_data[1]
        result = ClusterId(UserIdNo[1:-1])
    if str(command.strip().upper()) == "PEERLIST":
        print("Command Found : ",command)
        ClusterIdNo = extracted_data[1]
        result = PeerlistView(ClusterIdNo[1:-1])
    if str(command.strip().upper()) == "REQUESTMODEL":
        print("Command Found : ",command)
        reqDataPack = eval(decoded_data)
        # TaskQUEUE[reqDataPack[1][0]] = str(reqDataPack)
        TASKHOLDER.append([reqDataPack[1][0],str(reqDataPack)])
        result = [1,"Request Send"]
    if str(command.strip().upper()) == "SENDMODEL":
        print("Command Found : ",command)
        reqDataPack = eval(decoded_data)
        # TaskQUEUE[reqDataPack[-1]] = str(reqDataPack)
        TASKHOLDER.append([reqDataPack[-1],str(reqDataPack)])
        result = [1,"Request Fulfilled"]
    return str(result)

#cluser id finder
def ClusterId(userid):
    for device in DeviceTable:
        if device == userid:
             return [0,"Not having a Cluster. please wait..."]
    for cluster in ClusterTable:
        Culterpeerlist = ClusterTable[cluster]
        for peerid in Culterpeerlist:
            if peerid == userid:
                return ["CLUSTERID",cluster]

#peer list rectrived
def PeerlistView(TempClusterID):
    tempCluster = ClusterTable[TempClusterID]
    return ["PEERLIST",tempCluster]

#gebarate user id and clusterid
def generate_id(id_length=8):
    global existing_ids
    while True:
        # Generate a random ID string
        id_str = ''.join(random.choices(string.ascii_letters + string.digits, k=id_length))
        # Check if the ID is unique
        if id_str not in existing_ids:
            # Add the ID to the list of existing IDs
            existing_ids.append(id_str)
            return id_str

# This is the coroutine that will handle incoming client connections
async def handle_client(reader, writer):
    print('----------------------------------------------------------------')
    addr = writer.get_extra_info('peername')
    print('Connected by', addr)
    ##################USER_ID####################################
    userId = generate_id(16)
    print('User id : ', userId)
    writer.write(userId.encode())
    await writer.drain()
    #############################################################
    ##Clustering Process Start        ---------------------------
    ClusterId = generate_id(12)
    DeviceTable[userId] = ''
    if len(DeviceTable) >= clusterSize:
        my_list = []
        keyList = DeviceTable.keys()
        for key in keyList:
            my_list.append(key)
        ClusterTable[ClusterId] = my_list
        first_5_keys = list(DeviceTable.keys())[:5]
        for key in first_5_keys:
            del DeviceTable[key]
        print("Custer created : ",ClusterId," : ",my_list)
    ##Clustering Process END          ---------------------------
    ######################RUNNER_ENGINE##########################
    while True:
        #Task handler
        if len(TaskQUEUE) > 0:
            taskList = TaskQUEUE.keys()
            isFound = False
            for taskblockid in taskList:
                if userId == taskblockid:
                    tempdatBlock = eval(TaskQUEUE[taskblockid])
                    print("----task list : ",taskblockid," : ",TaskQUEUE[taskblockid])
                    tempResponse = str([tempdatBlock[0],tempdatBlock])
                    writer.write(tempResponse.encode())
                    await writer.drain()
                    isFound = True
            if isFound:
                del TaskQUEUE[userId]
        #Reciver handler
        try:
            data = await asyncio.wait_for(reader.read(51200), timeout=1)
        except asyncio.TimeoutError:
            continue
        if not data:
            break
        result = CommanManager(data, addr)
        writer.write(result.encode())
        await writer.drain()
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

#task asign handler on another thread
async def TaskSubmitter():
    while True:
        if len(TASKHOLDER) > 0:
            print("************************************************************")
            while TASKHOLDER:
                tempTask = TASKHOLDER.pop(0)
                if TaskQUEUE.get(tempTask[0]) is None:
                    evalTempTask = eval(tempTask[1])
                    TaskQUEUE[tempTask[0]] = str(tempTask[1])
                    print("task applyed")
                    print(evalTempTask[0]," : ",tempTask)
                else:
                    TASKHOLDER.append(tempTask)
                    break
            print("************************************************************")
        await asyncio.sleep(5)

# The following code runs the main coroutine as an asyncio task
if __name__ == "__main__":
    t = threading.Thread(target=asyncio.run, args=(TaskSubmitter(),))
    t.start()
    asyncio.run(main())
