import time
import base64
from PIL import Image
from soc9k import peerCom
from util import requestModel
from enumList import conctionType

TIMEOUT = 12 ## 12 => 60s
HOST = 'localhost'
#HOST = '13.250.112.193'
PORT = 9000
# MODE = conctionType.SHELL.value
MODE = conctionType.KERNEL.value
# MODE = conctionType.SEED.value

CLusterIDLoop = True
ModelParamLoop = True
TimerOut = 10

USERID = ""
CLUSTERID = ""
PEERLIST = []
MODELPARAMETERLIST = []
########################################################################
#------------------------------SAMPLE DATA-----------------------------#
genaratedDataPack  = bytes(1024)  # 1 KB
# genaratedDataPack  = bytes(1024*1024)  # 1 MB
MODELPARAMETERS = base64.b64encode(genaratedDataPack).decode('utf-8')
# MODELPARAMETERS = "sdhhfjksdhgkhskdghklsdhlgkdslkfhglk"
########################################################################


mySocket = peerCom(HOST, PORT, TIMEOUT)
USERID = mySocket.connect()
mySocket.start_receiver()
mySocket.start_sender()
print("USER TYPE  : ",MODE)
print("USER ID    : ",USERID)
################################################################################
#-----------------------BEGIN----COMMUNICATION SCRIPT--------------------------#
################################################################################
peerTypeReq = ["PEERTYPE",MODE]#-------------Cluster ID REQUEST-----------------
mySocket.request(requestModel(USERID,peerTypeReq))

while CLusterIDLoop: #----------------------GET Cluster-------------------------
    tempDataSet = mySocket.RECIVEQUE.copy()
    if len(tempDataSet) > 0:
        for x in tempDataSet:
            tempData = x.get("Data")
            if (tempData[0] == "CLUSTERID") & (tempData[2] == "PEERLIST"):
                mySocket.queueClean(x)
                CLUSTERID = tempData[1]
                PEERLIST = tempData[3]
                print("CLUSTER ID : ",CLUSTERID)
                print("PEER LIST  : ",PEERLIST)
                CLusterIDLoop = False
                break
if (MODE == conctionType.SEED.value) | (MODE == conctionType.KERNEL.value):
    for x in PEERLIST:#----------------------GET Model params-------------------
        if x != USERID:
            modelReq = ["MODELREQUEST"]
            mySocket.request(requestModel(USERID,modelReq,x))
    timerCal =0
    while ModelParamLoop:
        tempDataSet = mySocket.RECIVEQUE.copy()
        if len(tempDataSet) > 0:
            for x in tempDataSet:
                mySocket.queueClean(x)
                if x.get("Data")[0] == "MODELREQUEST":
                    print("MODEL REQUEST FROM : ",x.get("Sender"))
                    modelparameters = ["MODELPARAMETERS",MODELPARAMETERS]
                    mySocket.request(requestModel(USERID,modelparameters,x.get("Sender")))
                    print("MODEL PARAMETERS SEND TO : ",x.get("Sender"))
                elif x.get("Data")[0] == "MODELPARAMETERS":
                    print("MODEL PARAMETERS RECIVED FROM : ",x.get("Sender"))
                    MODELPARAMETERLIST.append(x)
                else:
                    print("UNKNOWN MESSAGE : ",x)
        time.sleep(1)
        timerCal +=1
        if timerCal == TimerOut:
            ModelParamLoop = False

################################################################################
#-------------------------END----COMMUNICATION SCRIPT--------------------------#
################################################################################
time.sleep(5)
mySocket.close()