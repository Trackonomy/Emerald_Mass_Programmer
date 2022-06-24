import requests
import json
import time

# qrs = ["18-280222-E30030",
#
# "18-280222-E30780",
#
# "18-280222-E30276",
#
# "18-280222-E30037",
#
# "18-280222-E30055",
#
# "18-280222-E30354",
#
# "18-280222-E30714",
#
# "18-280222-E30079",
#
# "18-280222-E30370",
#
# "18-280222-E30227"]

value = "18-280222-E29925"

gotten_qrs = []
#

qrs = []
def scanQRcodes():
    global  qrs
    # qrCodes = list(df['QR Code'])

    while True:
        if len(qrs) == 10:
            break
        qr = input("Scan Domino QR Code (enter 'q' when done scanning): ")
        if qr == 'q':
            break
        if not validateQR(qr):
            print("Not a valid Domino qrcode. Try again.")
            continue
        while qr in qrs:
            print("Duplicate QR detected, Please try again")
            qr = input("Scan Domino QR Code (enter 'q' when done scanning): ")
        qrs.append(qr)

def validateQR(qr):
    if len(qr) == 16 and qr.count('-') == 2 and qr[:2] == '18':
        return True

    return False
# for value in qrs:
#
#         print(requests.delete("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + value))_
scanQRcodes()
for qr in qrs:
        # while True:
    test = requests.get("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + qr)

    dom_record = json.loads(test.text)
# if dom_record != []:
#         gotten_qrs.append(dom_record[0]['qrcode'])
#         print(gotten_qrs)
# if dom_record != []:
    print(dom_record)
    # print(type(dom_record[0]['rssi']))
    # if dom_record[0]['status'] == 'success' and dom_record[0]['rssi']>-85:
    #     print('Pass')
    # if dom_record[0]['failed_reason'] == None:
    #     print('None')
    #     # time.sleep(30)


# ========================= 18-280222-E30030 Passes =========================
# ========================= 18-280222-E30780 Passes =========================
# ========================= 18-280222-E30276 Passes =========================
# ========================= 18-280222-E30037 Passes =========================
# ========================= 18-280222-E30055 Passes =========================
# ========================= 18-280222-E30354 Passes =========================
# ========================= 18-280222-E30714 Passes =========================
# ========================= 18-280222-E30079 Passes =========================
# ========================= 18-280222-E30370 Passes =========================
