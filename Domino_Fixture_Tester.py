import requests
import json
import time

# qrs = ["18-280222-E30045",
#
# "18-280222-E30435",
#
# "18-280222-E30288",
#
# "18-280222-E30077",
#
# "18-280222-E30010",
#
# "18-280222-E30051",
#
# "18-280222-E30254",
#
# "18-280222-E30417",
#
# "18-280222-E30257",
#
# "18-280222-E30227"]

value = "18-280222-E30057"

gotten_qrs = []
#
# for value in qrs:
#
#         print(requests.delete("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + value))_

# for qr in qrs:
while True:
        test = requests.get("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + value)

        dom_record = json.loads(test.text)
        # if dom_record != []:
        #         gotten_qrs.append(dom_record[0]['qrcode'])
        #         print(gotten_qrs)
        print(dom_record)
        time.sleep(30)
