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

macids = [] ## initialize macid list
qrCodes = [] ## initialize qr codes list
macqrpairs = {} ## initialize mac qr pair dict
flashed = False ## initialize DFU status
fw = '' ## fw to be flash

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
    return "{:012X}".format(int(mac, 16) + offset) ## function to increment macid by 1 in HEX

# This handles macid, flash bootloader, and the first DFU for emerald boards
def parallelDfu(chx, zipf, com, macAddy,active=True): ## function to call DFU command (channel, zip file, com port, mac address, run status)
    if active == True: #this is here to allow us an easy way of turning off a channel for testing

        for i in range(5):
            print("firing: ", i)
            try:
                os_cmd = 'nrfutil dfu ble -ic NRF52 -pkg ' + zipf + ' -p ' + com + ' -a ' + macAddy + ' -f -mtu 200' ## command to DFU by macid
                if os.system(os_cmd) != 0:
                    if i == 4:
                        # print('========================= ' + change_mac(macAddy, -1) + ' Fails =========================')

                        raise Exception('Ch' + str(chx) + ' error ') ## error if DFU is not successful after 4 attempts
                else:
                    listOfKeys = getKeysByValue(macqrpairs, change_mac(macAddy, -1))
                    for key in listOfKeys:
                        # print(key)
                        print('========================= ' + key + ' Passes =========================')
                    break
            except:
                # print('========================= ' + change_mac(macAddy, -1) + ' Fails =========================')
                print("#####An exception occurred with Ch " + str(chx))

def runDFU():
    global flashed, fw

    com = ['COM9','COM10','COM12','COM13','COM14','COM15','COM16','COM18','COM19','COM20'] ## com ports for NRF52-DK
    # com = ['COM9','COM12','COM18','COM19','COM20']
    DFU_processes = {} ## initialize dict to create DFU process based on # of qrCodes scanned
    fw = 'Em61x_MHM_LoRaWAN_V2.0.1_Final.zip' ## final fw
    # fw = 'Bat_Test.zip' ## low batt fw
    for p in range(len(macids)):
        DFU_processes["p{0}".format(p)] = multiprocessing.Process(name="p{0}".format(p), target=parallelDfu, args=(p+1, fw, com[p], macAddyincr[p], True)) ## create variables for multiprocessing based on len of macid
        (DFU_processes["p{0}".format(p)]).daemon = True
        (DFU_processes["p{0}".format(p)]).start()
    for o in range(len(macids)):
        (DFU_processes["p{0}".format(o)]).join()

    flashed = True ## finished flashing
    return flashed

####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################

def sendToArduino(sendStr):
    ser.write(bytes(sendStr, 'utf-8')) ## function to communicate with arduino


def run(on,off,start,finish,delaytime, start_stat = False,stop_stat = False): ## status for emags turning on and off triggered by Arduino (0, number of nodes, time emag is on)
    if start_stat:
        print("-----------------------------")
        for l in range(start,finish):
            print("Power {} for node {}".format(on,l+1))

    time.sleep(delaytime)
    if stop_stat:
        for y in range(start,finish):
            print("Power {} for node {}".format(off,y+1))

        print("-----------------------------")

if __name__ == '__main__':
    counter = 1
    while True:
        macAddyincr = [] ## macid hex increment initializer
        scanQRcodes() #function to validate then append qr codes to list
        for x in macids:
            macAddyincr.append(change_mac(x, 1)) ## increment macids by 1 in HEX
        # print(macids)
        # print(macAddyincr)
        startTime = time.time() ## test start time

        os.system("cls")
        print("/=======================================\\")
        print("| Starting TRACKONOMY Mass programmer (Final FW) |")
        print("========================================/")
        print("| 22/04/22 v1.0.0, TG |")
        print("\\=====================/")
        print("")
        numNodes = 10 ## number of magnets turning on

        serPort = "COM17" ## Serial port where arduino is connect
        baudRate = 9600 ## set baud rate
        ser = serial.Serial(serPort, baudRate)
        print("Serial port " + serPort + " opened  Baudrate " + str(baudRate))

        time.sleep(2) ## delay to get arduino ready
        # sendToArduino(str(len(macids)))
        print('Putting Nodes into DFU mode')
        sendToArduino(str(1)) ## Communicate with arduino to turn emags on
        run("on", "off", 0,numNodes, 20, True,True) ## run status of emags on for 20s then off
        runDFU() ## pass macids obtained from scanned QRs code to nrfutil commands to DFU as multiprocesses

        DFUrun = multiprocessing.Process(name="DFUrun", target=runDFU)
        wake_timer = multiprocessing.Process(name="wake_timer", target=run, args=("on", "on", 0, numNodes, 15, False, True))
        DFUrun.daemon = True
        wake_timer.daemon = True
        DFUrun.start()
        wake_timer.start()
        DFUrun.join()
        wake_timer.join()

        x = ser.readline() ##  read data sent from Arduino telling python it's ready for putting devices to sleep
        string_x = x.decode()
        stripped_string_x = string_x.strip() ## getting read arduino message into form that can be read as a string
        if stripped_string_x == "1" and flashed == True: ## If arduino is ready and flashing (DFU) is complete
            print("flashing complete.")
            print('Sleeping Nodes')
            sendToArduino(str(1)) ## Communicate with arduino to turn emags on
            # print('Sleeping Nodes')
            time.sleep(10)
            run("off","off",0,numNodes,0.01,True, False )
            ser.close() ## close serial port
        endTime = round((time.time() - startTime), 2) ## get run time of programming

        print(endTime, "seconds elapsed.")
        print("")
        lines = ["Test # {}".format(counter), '# of Domino(s): {}'.format(len(macids)),'Time taken: {}'.format(endTime),'FW: {}'.format(fw),'##################'] ## data for loggin
        with open('Logging.txt', 'a') as f: ## open txt file to write log to
            for line in lines:
                f.write(line) ## write the data in log file
                f.write('\n')
        counter = counter + 1
        macids = [] ## reset macid list for next test
        qrCodes = []  ## reset qr codes list for next test
        macqrpairs = {}  ## reset mac qr pair dict for next test
        flashed = False ## reset DFU status
        again_q = [
            inquirer.List(
                "Again",
                message="Select Y to run again or N to exit",
                choices=["Y", "N"],
                default=["Y"],
            ),
        ]
        again_a = inquirer.prompt(again_q) ## Ask user if they want to program more dominos
        if again_a['Again'] == "N":
            break
