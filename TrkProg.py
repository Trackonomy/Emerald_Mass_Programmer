import requests
import json
import serial
import time
from datetime import datetime
import os
import subprocess
import multiprocessing
import inquirer
from multiprocessing import Process, Manager
from subprocess import Popen
import csv


macids = [] ## initialize macid list
macidfails = []
qrCodes = [] ## initialize qr codes list
listOfKeys = list()
listOfKeys2 = list()
macqrpairs = {} ## initialize mac qr pair dict
qrorderpairs = {}
flashed = False ## initialize DFU status
fw = '' ## fw to be flash
errorList = 0

def sendToArduino(sendStr):
    ser.write(bytes(sendStr, 'utf-8')) ## function to communicate with arduino

def scanQRcodes():
    global macids, qrCodes, macqrpairs
    # qrCodes = list(df['QR Code'])

    previousDupe = False
    while True:
        if len(qrCodes) == 10:
            break
        if previousDupe == False:
            qr = input("Scan Domino QR Code (enter 'q' when done scanning): ")
        previousDupe = False
        if qr == 'q':
            break
        if qr == "":
            break
        if not validateQR(qr):
            print("Not a valid Domino qrcode. Try again.")
            continue
        while qr in qrCodes:
            print("Duplicate QR detected, Please try again")
            qr = input("Scan Domino QR Code (enter when done): ")
            previousDupe = True
        if previousDupe == False:
            qrCodes.append(qr)
            qrorderpairs[len(qrCodes)] = qr
        
def get_macs(qr_list):
    macids.clear()
    global errorList
    print("")
    print(f"Receiving data on each QR Code...{len(qr_list)} Total...")
    #print(qr_list)
    print("")
    print("============================================")
    print(" Node        QR                 MAC")
    print("============================================")
    for qr in qr_list:
        try:
            url = "http://vmprdate.eastus.cloudapp.azure.com:9000/api/v1/manifest/?qrcode=" + qr
            r = requests.get(url)
            rawjson = json.loads(r.text)

            data = []
            if rawjson['error'] == False:
                data = rawjson['data']
                macid = data[0]['macid']
                macqrpairs[qr] = macid
                print(f" ({len(macids)+1}){qr:>25}   {macid}")
                if macid != "None" and macid != "":
                    macids.append(macid)
                else:
                    print("MAC ID not found for ",qr)
                    continue
                serverResponse = json.dumps(data)
            if rawjson['error'] == True:
                print(f" (X){qr:>25}   {rawjson}")
                macqrpairs[qr] = "No Record"
                errorList += 1

        except Exception as e:
            print("Error Occured\n")
            print(e)
    print("============================================")
    #waitForInput = input("Press Enter to Continue...")
    
def validateQR(qr):
    if len(qr) == 16 and qr.count('-') == 2 and qr[:2] == '18':
        return True

    return False
    
def change_mac(mac, offset):
    if mac == "No Record":
        return
    else:
        return "{:012X}".format(int(mac, 16) + offset) ## function to increment macid by 1 in HEX
    
def setMags(on,off,start,finish,delaytime,start_stat=False,stop_stat=False): ## status for emags turning on and off triggered by Arduino (0, number of nodes, time emag is on)
    if start_stat:
        print("-----------------------------")
        for l in range(start,finish):
            print(f" Power {on} node {l+1}: {macids[l]}")
        ser.write(b'2') ## Communicate with arduino to turn emags on     
    print("")
    print(f" Waiting {delaytime} second(s)...")
    print("")
    time.sleep(delaytime)
    if stop_stat:
        for y in range(start,finish):
            print(f" Power {off} node {y+1}: {macids[y]}")
        ser.write(b'3') ## Communicate with arduino to turn emags off    
        print("-----------------------------")
        
def parallelDfu(passedmacs,chx, zipf, com, macAddy,active=True): ## function to call DFU command (channel, zip file, com port, mac address, run status)
    global listOfKeys
    
    if active == True: #this is here to allow us an easy way of turning off a channel for testing
        for i in range(5):
            print(f"{macAddy} DFU Attempt {i} on Ch {chx} COM {com}")
            try:
                os_cmd = 'nrfutil dfu ble -ic NRF52 -pkg ' + zipf + ' -p ' + com + ' -a ' + macAddy + ' -f -mtu 200' ## command to DFU by macid
                if os.system(os_cmd) != 0:
                    if i == 4:
                        print(f"DFU for {macAddy} not successful on attempt {i}.")
                        raise Exception('Ch' + str(chx) + ' error ') ## error if DFU is not successful after 4 attempts
                else:
                    #passedmacs.append(change_mac(macAddy,-1))
                    print(f"DFU for {macAddy} successful on attempt {i}.")
                    break
            except:
                # print('========================= ' + change_mac(macAddy, -1) + ' Fails =========================')
                print("ALERT - An exception occurred with Ch " + str(chx))
    i = 0

def runDFU():
    global flashed, fw
    flashed = False
    DFU_processes = {} ## initialize dict to create DFU process based on # of qrCodes scanned
    fw = 'Em61x_MHM_LoRaWAN_V2.2.7.zip' ## final fw
    # fw = 'Bat_Test.zip' ## low batt fw
    print(com[0])
    for p in range(len(macAddyincr)):
        DFU_processes["p{0}".format(p)] = multiprocessing.Process(name="p{0}".format(p), target=parallelDfu, args=(passedmacs,p+1, fw, com[p], macAddyincr[p], True)) ## create variables for multiprocessing based on len of macid
        (DFU_processes["p{0}".format(p)]).daemon = True
        (DFU_processes["p{0}".format(p)]).start()

    for o in range(len(macAddyincr)):
        (DFU_processes["p{0}".format(o)]).join()

    flashed = True ## finished flashing
    return flashed
    
def toggle(cycles,sleepTime):
    for i in range(cycles):
        setMags("on","off",0,numNodes, sleepTime, True,True)
        time.sleep(sleepTime)

log_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

if __name__ == '__main__':
    counter = 1
    serPort = None
    
    com = ['COM9', 'COM10','COM11','COM12']  ## com ports for NRF52-DK at SJ
    #com = ['9','10','11','12']  ## com ports for NRF52-DK at SJ
    serPort = "COM8"  ## Serial port where arduino is connect
    
    
    try:
        with open(log_dir + '\\Log' + datetime.today().strftime('%Y%m%d') + '.csv', 'r+', newline='') as csvfile:
            print(".csv already exists")
            csv.reader(csvfile)
    except:
        with open(log_dir+'\\Log' + datetime.today().strftime('%Y%m%d') + '.csv', 'a+', newline='') as csvfile:
            print("Creating new .csv")
            topfields = ['Time', 'QR', 'MAC ID', 'DFU Status']
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(topfields)

    while True:
        errorList = 0
        manager = Manager()
        passedmacs = manager.list()
        passedqrs = []     
        macAddyincr = [] ## macid hex increment initializer
        failedqrs = []
        sys_test_fails = []
        gotten_qrs = []
        scanQRcodes() #function to validate then append qr codes to list
        get_macs(qrCodes)
        for x in macids:
            macAddyincr.append(change_mac(x, 1)) ## increment macids by 1 in HEX
        startTime = time.time() ## test start time
        numNodes = len(macids)## number of magnets turning on

        baudRate = 9600 ## set baud rate
        ser = serial.Serial(serPort, baudRate)
        print(" Serial port " + serPort + " opened  Baudrate " + str(baudRate))

        time.sleep(2) ## delay to get arduino ready
        
        print(' Putting Nodes into DFU mode')
        #ser.write(b'0') ## Communicate with arduino to turn emags on     
        toggle(4,1)
        
        time.sleep(2)
        
        runDFU() ## pass macids obtained from scanned QRs code to nrfutil commands to DFU as multiprocesses

        for macs in passedmacs:
            getKeysByValue(macqrpairs, macs)
        passedqrs = listOfKeys
        

        first_DFU_fail = list(set(qrCodes)-set(passedqrs))
        print(" Setting Sleep Magnet(s) High...")
        print("-----------------------------")
        setMags("on","off",0,numNodes, 30, True,True)
        print("-----------------------------")

        endTime = round((time.time() - startTime), 2) ## get run time of programming
        #print(endTime, "seconds elapsed.")      
        #print("")    
        print(f" DFU Session {counter} - {len(macids)+errorList} Domino(s) -  Time taken: {endTime}s - FW: {fw}")
        print("-----------------------------")
        print(f"  Number of successful DFUs: {len(passedmacs)}")      
        print(f"      Number of failed DFUs: {len(macids)-len(passedmacs) + errorList}")
        print("-----------------------------")
        print("")
        
        print(" Closing serial port...")
        ser.close()  ## close serial port

        counter = counter + 1
        macids.clear() ## reset macid list for next test
        qrCodes.clear()  ## reset qr codes list for next test
        macqrpairs.clear()  ## reset mac qr pair dict for next test
        passedqrs.clear()
        failedqrs.clear()
        passedmacs[:] = []
        gotten_qrs.clear()
        macAddyincr.clear()
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