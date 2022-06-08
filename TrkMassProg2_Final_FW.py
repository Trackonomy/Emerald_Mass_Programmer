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
qrCodes = [] ## initialize qr codes list
listOfKeys = list()
listOfKeys2 = list()
macqrpairs = {} ## initialize mac qr pair dict
qrorderpairs = {}
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
        qrorderpairs[len(qrCodes)] = qr

def get_macs(qr_list):
    macids.clear()
    print("Receiving data on each QR Code...")
    for qr in qr_list:
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
    listOfItems = dictOfElements.items()
    for item in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return listOfKeys

# ======================================================================================================================

def change_mac(mac, offset):
    return "{:012X}".format(int(mac, 16) + offset) ## function to increment macid by 1 in HEX

# This handles macid, flash bootloader, and the first DFU for emerald boards
def parallelDfu(passedmacs,chx, zipf, com, macAddy,active=True): ## function to call DFU command (channel, zip file, com port, mac address, run status)
    global listOfKeys
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
                    passedmacs.append(change_mac(macAddy,-1))
                    # print(change_mac(macAddy,-1))
                    break
            except:
                # print('========================= ' + change_mac(macAddy, -1) + ' Fails =========================')
                print("#####An exception occurred with Ch " + str(chx))
    i = 0

def runDFU():
    global flashed, fw
    flashed = False
    DFU_processes = {} ## initialize dict to create DFU process based on # of qrCodes scanned
    fw = 'Em61x_MHM_LoRaWAN_V2.0.1_Final.zip' ## final fw
    # fw = 'Bat_Test.zip' ## low batt fw

    for p in range(len(macAddyincr)):
        DFU_processes["p{0}".format(p)] = multiprocessing.Process(name="p{0}".format(p), target=parallelDfu, args=(passedmacs,p+1, fw, com[p], macAddyincr[p], True)) ## create variables for multiprocessing based on len of macid
        (DFU_processes["p{0}".format(p)]).daemon = True
        (DFU_processes["p{0}".format(p)]).start()

    for o in range(len(macAddyincr)):
        (DFU_processes["p{0}".format(o)]).join()

    flashed = True ## finished flashing
    return flashed

####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################

def sendToArduino(sendStr):
    ser.write(bytes(sendStr, 'utf-8')) ## function to communicate with arduino

def delete_records(qrs):
    for value in qrs:
            print('-----------------Deleting recording for {}'.format(value))
            print(requests.delete("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + value))
def get_systest_records(qrs):
    gotten_qrs.clear()
    for qr in qrs:
        test = requests.get("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + qr)

        dom_record = json.loads(test.text)
        if dom_record != []:
            print('QR code: {} | blacklist: {} | Test Status: {} \n'.format(str(dom_record[0]['qrcode']),str(dom_record[0]['blacklisted']),str(dom_record[0]['status'])))
            if dom_record[0]['status'] == 'success':
                gotten_qrs.append(dom_record[0]['qrcode'])

def run(on,off,start,finish,delaytime,start_stat=False,stop_stat=False): ## status for emags turning on and off triggered by Arduino (0, number of nodes, time emag is on)
    if start_stat:
        print("-----------------------------")
        for l in range(start,finish):
            print("Power {} for node {}".format(on,l+1))

    time.sleep(delaytime)
    if stop_stat:
        for y in range(start,finish):
            print("Power {} for node {}".format(off,y+1))

        print("-----------------------------")
def databaseSendData(params):
    MFDB_ENDPOINT = "http://manufscan.eastus.cloudapp.azure.com/manuf"
    endpoint = MFDB_ENDPOINT
    headers = {}
    try:
        r = requests.post(url = endpoint, headers = headers, data=params)
        return r
    except:
        print('Something went wrong with sending data to MFDB...')

def csv_write(test_data):
    with open(log_dir+'\\Log' + datetime.today().strftime('%Y%m%d') + '.csv', 'a+', newline='') as csvfile:
        # topfields = ['qrcode','macid','Pass/Fail','RSSI','Failure Reason']
        csvwriter = csv.writer(csvfile)
        # csvwriter.writerow(topfields)
        csvwriter.writerow(test_data)


if __name__ == '__main__':
    counter = 1

    facility_q =  [inquirer.List(
                "Facility",
                message="Select Facility you are at",
                choices=["Juarez", "San Jose"],
                default=["Juarez"],
            ),
        ]
    facility_a = inquirer.prompt(facility_q) ## Ask user if they want to program more dominos
    if facility_a['Facility'] == "San Jose":
        # com = ['COM9', 'COM10', 'COM12', 'COM13', 'COM14', 'COM15', 'COM16', 'COM18', 'COM19','COM20']  ## com ports for NRF52-DK at SJ
        # serPort = "COM4"  ## Serial port where arduino is connect
        com = ['COM5','COM6','COM7','COM8']  ## com ports for NRF52-DK at SJ
        serPort = "COM4"  ## Serial port where arduino is connect
        log_dir = r"C:\\Users\\TanishGupta\\OneDrive - Trackonomy\\Desktop"
    elif facility_a['Facility'] == "Juarez":
        com = ['COM3', 'COM4', 'COM5', 'COM7', 'COM8', 'COM9', 'COM11', 'COM12','COM13','COM14']  ## com ports for NRF52-DK at SJ
        serPort = "COM6"  ## Serial port where arduino is connect
        log_dir = r"C:\\Users\\PRODUCCION ISM\\Desktop\\Logs"

    try:
        with open(log_dir+'\\Log' + datetime.today().strftime('%Y%m%d') + '.csv', 'r+', newline='') as csvfile:
            csv.reader(csvfile)
    except:
        with open(log_dir+'\\Log' + datetime.today().strftime('%Y%m%d') + '.csv', 'a+', newline='') as csvfile:
            topfields = ['qrcode', 'macid', 'Pass/Fail', 'RSSI', 'Failure Reason']
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(topfields)

    while True:
        manager = Manager()
        passedmacs = manager.list()
        passedqrs = []
        macAddyincr = [] ## macid hex increment initializer
        failedqrs = []
        sys_test_fails = []
        gotten_qrs = []
        scanQRcodes() #function to validate then append qr codes to list
        get_macs(qrCodes)
        delete_records(qrCodes)
        for x in macids:
            macAddyincr.append(change_mac(x, 1)) ## increment macids by 1 in HEX
        startTime = time.time() ## test start time

        os.system("cls")
        print("/================================================\\")
        print("| Starting TRACKONOMY Mass programmer (Final FW) |")
        print("================================================/")
        print("                | 22/04/22 v1.0.0, TG |          ")
        print("\\=============================================/")
        print("")
        numNodes = len(macids)## number of magnets turning on

        baudRate = 9600 ## set baud rate
        ser = serial.Serial(serPort, baudRate)
        print("Serial port " + serPort + " opened  Baudrate " + str(baudRate))

        time.sleep(2) ## delay to get arduino ready
        # sendToArduino(str(len(macids)))
        print('Putting Nodes into DFU mode')
        ser.write(b'0') ## Communicate with arduino to turn emags on
        run("on","off", 0,numNodes, 20, True,True) ## run status of emags on for 20s then off
        runDFU() ## pass macids obtained from scanned QRs code to nrfutil commands to DFU as multiprocesses
        # print("==============================================Test 1 results================================================")
        for macs in passedmacs:
            getKeysByValue(macqrpairs, macs)
        passedqrs = listOfKeys
        first_DFU_fail = list(set(qrCodes)-set(passedqrs))
        print('Waiting for System test results........................................................... ')
        while True:
            get_systest_records(passedqrs)
            print('Got Record for {}/{} unit(s)'.format(len(gotten_qrs),len(passedqrs)))
            ask_finish = input('Hit q to run again or p to continue: ')
            if ask_finish == 'q':
                # gotten_qrs.clear()
                print('\n')
                get_systest_records(passedqrs)
                print('Got Record for {}/{} unit(s)\n'.format(len(gotten_qrs), len(passedqrs)))
                ask_finish = input('Hit q to run again or p to continue: ')
            if ask_finish == 'p':
                # print(list(set(qrCodes).difference(gotten_qrs)))
                if list(set(passedqrs).difference(gotten_qrs)) != []:
                    for i in list(set(passedqrs).difference(gotten_qrs)):
                        sys_test_fails.append(i)
                        test = requests.get(
                            "https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + i)

                        dom_record = json.loads(test.text)
                        if dom_record !=[]:
                            keys = [k for k, v in qrorderpairs.items() if v == i]
                            print("--------------------- {} Fails System Test | Reason: {} | remove unit {} --------------------".format( i, dom_record[0]['failed_reason'],str(keys[0])))

                            failed_reason_str = dom_record[0]['failed_reason'].replace(" ", "")
                            reason_list = failed_reason_str.split(":")
                            reasons = ""
                            for n in range(1, len(reason_list), 2):
                                if "F" in reason_list[n]:
                                    if reasons == "":
                                        reasons = reason_list[n-1][0] + "1"
                                    else:
                                        reasons += "|" + reason_list[n-1][0] + "1"

                            result_data = {
                                "UnitID": i,

                                "MachineID": "Dom_Sys_Test",

                                "UnitScanTime": datetime.now().isoformat()[:23],

                                "MachineScanTime": datetime.now().isoformat()[:23],

                                "OperatorID": str(macqrpairs[i]),

                                "ActivityDetails": "F|{}|{}".format(dom_record[0]['rssi'], reasons)

                            }
                            csv_write([i,macqrpairs[i],'Fail',dom_record[0]['rssi'],dom_record[0]['failed_reason']])
                            # print(result_data)
                            __resp = databaseSendData(result_data)
                        else:
                            keys = [k for k, v in qrorderpairs.items() if v == i]
                            print("--------------------- {} Fails System Test | Reason: {} | remove unit {} --------------------".format(i,'No Record', str(keys[0])))

                            result_data = {
                                "UnitID": i,

                                "MachineID": "Dom_Sys_Test",

                                "UnitScanTime": datetime.now().isoformat()[:23],

                                "MachineScanTime": datetime.now().isoformat()[:23],

                                "OperatorID": str(macqrpairs[i]),

                                "ActivityDetails": "F|{}".format('No Record')

                            }
                            csv_write([i, macqrpairs[i], 'Fail', 'NA', 'No Record Found'])
                            __resp = databaseSendData(result_data)
                            # print(result_data)
                        print('\n')
                        keys.clear()
                if first_DFU_fail != []:
                    for i in first_DFU_fail:
                        keys_again = [k for k, v in qrorderpairs.items() if v == i]
                        print("--------------------- {} Fails First DFU | remove unit {} --------------------".format(i,str(keys_again[0])))
                        test = requests.get(
                            "https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + i)

                        dom_record = json.loads(test.text)
                        result_data = {
                            "UnitID": i,

                            "MachineID": "Dom_Sys_Test",

                            "UnitScanTime": datetime.now().isoformat()[:23],

                            "MachineScanTime": datetime.now().isoformat()[:23],

                            "OperatorID": str(macqrpairs[i]),

                            "ActivityDetails": 'Failed First DFU'

                        }
                        csv_write([i, macqrpairs[i], 'Fail', 'NA', 'Failed First DFU'])
                        __resp = databaseSendData(result_data)
                        # print(result_data)
                        print('\n')
                        keys_again.clear()
                qrCodes = list(set(qrCodes) - set(sys_test_fails))
                qrCodes = list(set(qrCodes) - set(first_DFU_fail))
                print('\n')
                break

        sys_test_complete = input('Please remove failed units and input "q" to continue: ')

        if sys_test_complete == 'q' and flashed:
            macAddyincr.clear()
            for x in qrCodes:
                macAddyincr.append(change_mac(macqrpairs[x], 1))  ## increment macids by 1 in HEX
            print(macAddyincr)
            passedmacs[:] = []
            passedqrs.clear()
            failedqrs.clear()
            listOfKeys.clear()
            ser.write(b'1')
            for i in range(3):
                run("on","off",0,numNodes, 2, True,True)
                time.sleep(2)
            ser.write(b'2')

            if macAddyincr:
                runDFU()

                if flashed:
                    print("flashing complete.")
                    print('Sleeping Nodes')
                    time.sleep(20)
                    ser.write(b'3')
                    run("off", "off", 0, numNodes, 0, True, False)
            else:
                pass
            ser.close()  ## close serial port

            endTime = round((time.time() - startTime), 2) ## get run time of programming

            print(endTime, "seconds elapsed.")
            print("==============================================DFU results================================================")
            for macs in passedmacs:
                getKeysByValue(macqrpairs, macs)
            passedqrs = listOfKeys
            failedqrs = list(set(qrCodes) - set(passedqrs))
            for key in passedqrs:
                passkeys = [k for k, v in qrorderpairs.items() if v == key]
                print('========================= ' + str(key) + ' Passes  | Unit: ' + str(passkeys[0]) + ' =========================')
                test = requests.get(
                    "https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + key)

                dom_record = json.loads(test.text)
                result_data = {
                    "UnitID": key,

                    "MachineID": "Dom_Sys_Test",

                    "UnitScanTime": datetime.now().isoformat()[:23],

                    "MachineScanTime": datetime.now().isoformat()[:23],

                    "OperatorID": str(macqrpairs[key]),

                    "ActivityDetails": "P|{}".format(dom_record[0]['rssi'])

                }
                csv_write([key, macqrpairs[key], 'Pass', dom_record[0]['rssi'], 'NA'])
                __resp = databaseSendData(result_data)
                # print(result_data)
                passkeys.clear()
            for key in failedqrs:
                failkeys = [k for k, v in qrorderpairs.items() if v == key]
                test = requests.get(
                    "https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + key)
                dom_record = json.loads(test.text)
                try:
                    print('========================= {} Fails | Reason: {} | Unit: {} ========================='.format(str(key),dom_record[0]['failed_reason'],str(failkeys[0])))

                    failed_reason_str = dom_record[0]['failed_reason'].replace(" ", "")
                    reason_list = failed_reason_str.split(":")
                    reasons = ""
                    for n in range(1, len(reason_list), 2):
                        if "F" in reason_list[n]:
                            if reasons == "":
                                reasons = reason_list[n - 1][0] + "1"
                            else:
                                reasons += "|" + reason_list[n - 1][0] + "1"

                    result_data = {
                        "UnitID": key,

                        "MachineID": "Dom_Sys_Test",

                        "UnitScanTime": datetime.now().isoformat()[:23],

                        "MachineScanTime": datetime.now().isoformat()[:23],

                        "OperatorID": str(macqrpairs[key]),

                        "ActivityDetails": "F-Sleep|{}|{}".format(dom_record[0]['rssi'], reasons)

                    }
                    csv_write([key, macqrpairs[Key], 'Fail', dom_record[0]['rssi'], '{} | {}'.format(dom_record[0]['failed_reason'],'Fail Sleep')])
                    __resp = databaseSendData(result_data)
                    # print(result_data)
                except:
                    print('========================= {} Fails | Reason: {} | Unit: {} ========================='.format(str(key), 'Failed 2nd DFU', str(failkeys[0])))
                    result_data = {
                        "UnitID": key,

                        "MachineID": "Dom_Sys_Test",

                        "UnitScanTime": datetime.now().isoformat()[:23],

                        "MachineScanTime": datetime.now().isoformat()[:23],

                        "OperatorID": str(macqrpairs[key]),

                        "ActivityDetails": "F-Sleep|{}|{}".format(dom_record[0]['rssi'],'Failed 2nd DFU')

                    }
                    csv_write([key, macqrpairs[key], 'Fail', dom_record[0]['rssi'], 'Failed 2nd DFU'])
                    __resp = databaseSendData(result_data)
                    # print(result_data)
                failkeys.clear()
            # print(passedqrs)
            print(passedmacs)
            print("")
            lines = ["Test # {}".format(counter), '# of Domino(s): {}'.format(len(macids)),'Time taken: {}'.format(endTime),'FW: {}'.format(fw),'###############################'] ## data for loggin
            with open(log_dir+'\\Log_'+datetime.today().strftime('%Y%m%d')+'.txt', 'a+') as f: ## open txt file to write log to
                for line in lines:
                    f.write(line) ## write the data in log file
                    f.write('\n')
                for i in passedqrs:
                    f.write('{} Passes '.format(i))
                    f.write('\n')
                for i in failedqrs:
                    f.write('{} Fails'.format(i))
                    f.write('\n')
                f.write('############################################')
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
