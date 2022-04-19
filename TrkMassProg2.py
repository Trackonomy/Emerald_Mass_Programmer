import requests
import json
import serial
import time
import os
import subprocess
import multiprocessing
import inquirer
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

def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys
# ======================================================================================================================

def change_mac(mac, offset):
    return "{:012X}".format(int(mac, 16) + offset)

# This handles macid, flash bootloader, and the first DFU for emerald boards
def parallelDfu(chx, zipf, com, macAddy,active=True):
    if active == True: #this is here to allow us an easy way of turning off a channel for testing

        for i in range(1):
            print("firing: ", i)
            try:
                os_cmd = 'nrfutil dfu ble -ic NRF52 -pkg ' + zipf + ' -p ' + com + ' -a ' + macAddy + ' -f -mtu 200'
                if os.system(os_cmd) != 0:
                    if i == 4:
                        raise Exception('Ch' + str(chx) + ' error ')
                else:
                    break
            except:
                print("#####An exception occurred with Ch " + str(chx))

def runDFU():
    global flashed

    com = ['COM9','COM10','COM12','COM13','COM14','COM15','COM16','COM18','COM19','COM20']
    # com = ['COM9','COM12','COM18','COM19','COM20']
    DFU_processes = {}
    fw = 'Em61x_MHM_LoRaWAN_V2.0.1_Final.zip'
    # fw = 'Bat_Test.zip'
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
def sendToArduino(sendStr):
    ser.write(bytes(sendStr, 'utf-8'))


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
    # endTime = round((time.time() - startTime), 2)
    # # print("Done...How did we do?")
    # # print("")
    # print(endTime, "seconds elapsed.")
    # print("")
    # ser.close()

if __name__ == '__main__':
    counter = 1
    while True:
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

        time.sleep(2)
        # sendToArduino(str(len(macids)))
        print('Putting Nodes into DFU mode')
        sendToArduino(str(1))
        run(0,numNodes,20)
        runDFU()
        x = ser.readline()
        string_x = x.decode()
        stripped_string_x = string_x.strip()
        if stripped_string_x == "1" and flashed == True:
            print("flashing complete.")
            print('Sleeping Nodes')
            sendToArduino(str(1))
            run(0, numNodes, 15)
            ser.close()
        endTime = round((time.time() - startTime), 2)

        print(endTime, "seconds elapsed.")
        print("")
        lines = ["Test # {}".format(counter), '# of Domino(s): {}'.format(len(macids)),'Time taken: {}'.format(endTime),'##################']
        with open('Logging.txt', 'a') as f:
            for line in lines:
                f.write(line)
                f.write('\n')
        counter = counter + 1
        macids = []
        qrCodes = []
        macqrpairs = {}
        flashed = False
        again_q = [
            inquirer.List(
                "Again",
                message="Select Y to run again or N to exit",
                choices=["Y", "N"],
                default=["Y"],
            ),
        ]
        again_a = inquirer.prompt(again_q)
        if again_a['Again'] == "N":
            break
