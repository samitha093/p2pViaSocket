import signal
import sys
import time
from soc9k import peerCom
from enumList import conctionType
from com import communicationProx
from seed import seedProx

HOST = 'localhost'  #'13.250.112.193'
PORT = 9000

########################################################################
#------------------------------PEER   DATA-----------------------------#
MODELPARAMETERS  = bytes(1024)  # 1 KB
# MODELPARAMETERS  = bytes(100*1024)  # 100 KB
# MODELPARAMETERS  = bytes(1024*1024)  # 1 MB
# MODELPARAMETERS  = bytes(3*1024*1024)  # 3 MB
# MODELPARAMETERS  = bytes(5*1024*1024)  # 5 MB
########################################################################

########################################################################
#------------------------------MOBILE MODEL----------------------------#
MOBILEMODELPARAMETERS  = bytes(1024)  # 1 KB
########################################################################

def sigint_handler(signal, frame, mySocket):
    print('Exiting program...')
    mySocket.close(0)
    sys.exit(0)

def mainFunn(MODE, TIMEOUT = 12, RECIVER_TIMEOUT = 50, SHELL_TIMEOUT = 300):
    mySocket = peerCom(HOST, PORT, TIMEOUT , MODE)
    signal.signal(signal.SIGINT, lambda signal, frame: sigint_handler(signal, frame, mySocket))
    USERID = mySocket.connect()
    mySocket.start_receiver()
    mySocket.start_sender()
    print("USER TYPE  : ",MODE)
    print("USER ID    : ",USERID)
    if MODE == conctionType.KERNEL.value:
        MODELPARAMETERLIST = communicationProx(mySocket,USERID,MODE,RECIVER_TIMEOUT,MODELPARAMETERS)
    if MODE == conctionType.SHELL.value:
        seedProx(mySocket,USERID,MODE,MOBILEMODELPARAMETERS,MODELPARAMETERS,SHELL_TIMEOUT)

#Call from Separat thread
if __name__ == "__main__":
    mainFunn("KERNEL")
    time.sleep(2)
    print("loop call triggered")
