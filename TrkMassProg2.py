import requests
import json
import serial
import time
import os
import subprocess
import multiprocessing


from multiprocessing import Process, Manager
from subprocess import Popen

macids = []
qrCodes = []
macqrpairs = {}
flashed = False
def scanQRcodes():
    global macids, qrCodes, macqrpairs
    # qrCodes = list(df['QR Code'])

    while True:
        if len(qrCodes) == 10:
            break
        qr = input("Scan Domino QR Code (enter 'q' when done scanning): ")
        if qr == 'q':
            break
        if not validateQR(qr):
            print("Not a valid Domino qrcode. Try again.")
            continue
        while qr in qrCodes:
            print("Duplicate QR detected, Please try again")
            qr = input("Scan Domino QR Code (enter 'q' when done scanning): ")
        qrCodes.append(qr)
        print(len(qrCodes))
    print("Receiving data on each QR Code...")
    for qr in qrCodes:
        try:
            # get data on entered qr code from database
            url = "http://vmprdate.eastus.cloudapp.azure.com:9000/api/v1/manifest/?qrcode=" + qr
            r = requests.get(url)
            rawjson = json.loads(r.text)

            # get data from entered qr code
            data = []
            if rawjson['error'] == False:
                data = rawjson['data']

                macid = data[0]['macid']
                macqrpairs[qr] = macid
                # print(macid)
                if macid != "None" and macid != "":
                    macids.append(macid)
                else:
                    print("Macid not found for ",qr)
                    continue
                serverResponse = json.dumps(data)

        except Exception as e:
            print("Error Occured\n")
            print(e)
def validateQR(qr):
    if len(qr) == 16 and qr.count('-') == 2 and qr[:2] == '18':
        return True

    return False


def sendToArduino(sendStr):
    ser.write(bytes(sendStr,'utf-8'))
# ======================================

# def recvFromArduino():
#     global startMarker, endMarker
#
#     ck = ""
#     x = "z"
#     byteCount = -1
#
#     while ord(x) != startMarker:
#         x = ser.read()
#
#     while ord(x) != endMarker:
#         if ord(x) != startMarker:
#             ck = ck + x.decode("utf-8")
#             byteCount += 1
#         x = ser.read()
#
#     return (ck)


# ============================

# def waitForArduino():
#     global startMarker, endMarker
#
#     msg = ""
#     while msg.find("Arduino is ready") == -1:
#
#         while ser.inWaiting() == 0:
#             pass
#
#         msg = recvFromArduino()
#
#         print(msg)
#         print()

# def runTest(td):
#     numLoops = len(td)
#     waitingForReply = False
#
#     n = 0
#     while n < numLoops:
#         teststr = td[n]
#
#         if waitingForReply == False:
#             sendToArduino(teststr)
#             waitingForReply = True
#         waitingForReply = False
#         n += 1
#
#         if waitingForReply == True:
#
#             while ser.inWaiting() == 0:
#                 pass
#
#             dataRecvd = recvFromArduino()
#             print("Reply Received  " + dataRecvd)
#             n += 1
#             waitingForReply = False
#
#             print("===========")
# ======================================
def change_mac(mac, offset):
    return "{:012X}".format(int(mac, 16) + offset)

# This handles macid, flash bootloader, and the first DFU for emerald boards
def parallelDfu(chx, zipf, com, macAddy,active=True):
    if active == True: #this is here to allow us an easy way of turning off a channel for testing

        for i in range(5):
            print("firing: ", i)
            try:
                os_cmd = 'nrfutil dfu ble -ic NRF52 -pkg ' + zipf + ' -p ' + com + ' -a ' + macAddy + ' -f -mtu 200'
                if os.system(os_cmd) != 0:
                    if i == 4:
                        raise Exception('Ch' + str(chx) + ' error ' )
                else:
                    break
            except:
                print("#####An exception occurred with Ch " + str(chx) )

def runDFU():
    global flashed

    com = ['COM9','COM10','COM12','COM13','COM14','COM15','COM16','COM18','COM19','COM20']
    # com = ['COM9','COM12','COM18','COM19','COM20']
    DFU_processes = {}
    # fw = 'Em61x_MHM_LoRaWAN_V2.0.1_Final.zip'
    fw = 'Bat_Test.zip'
    for p in range(len(macids)):
        DFU_processes["p{0}".format(p)] = multiprocessing.Process(name="p{0}".format(p), target=parallelDfu, args=(p+1, fw, com[p], macAddyincr[p], True))
        (DFU_processes["p{0}".format(p)]).daemon = True
        (DFU_processes["p{0}".format(p)]).start()
    for o in range(len(macids)):
        (DFU_processes["p{0}".format(o)]).join()

    flashed = True
    return flashed
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################

def run(start,finish,delaytime):

    print("-----------------------------")
    for l in range(start,finish):
        # print("Toggling EM", emToggles, "times.")
        # time.sleep(1)

        print("Power on for node ",l+1)
        # testData = ["1"]
        # runTest(testData)

    time.sleep(delaytime)
    for y in range(start,finish):
        print("Power off for node",y+1)

    print("-----------------------------")

    endTime = round((time.time() - startTime), 2)
    # print("Done...How did we do?")
    # print("")
    print(endTime, "seconds elapsed.")
    print("")
    # ser.close()
if __name__ == '__main__':
    macAddyincr = []
    scanQRcodes()
    for x in macids:
        macAddyincr.append(change_mac(x, 1))
    # print(macids)
    # print(macAddyincr)
    startTime = time.time()

    os.system("cls")
    print("/=======================================\\")
    print("| Starting TRACKONOMY Mass programmer |")
    print("========================================/")
    print("| 22/04/15 v1.0.0, TG |")
    print("\\=====================/")
    print("")
    numNodes = 10

    serPort = "COM17"
    baudRate = 9600
    ser = serial.Serial(serPort, baudRate)
    print("Serial port " + serPort + " opened  Baudrate " + str(baudRate))

    # startMarker = 60
    # endMarker = 62
    # waitForArduino()
    time.sleep(2)
    sendToArduino(str(1))

    run(0,numNodes,20)
    # time.sleep(15)
    runDFU()
    x = ser.readline()
    string_x = x.decode()
    stripped_string_x = string_x.strip()
    if stripped_string_x == "1" and flashed == True:
        print("flashing complete.")
        sendToArduino(str(1))
        run(0, numNodes, 15)
        ser.close()

