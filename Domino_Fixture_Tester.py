import requests
import json


qrs = ["18-280222-E30045",

"18-280222-E30435",

"18-280222-E30288",

"18-280222-E30077",

"18-280222-E30010",

"18-280222-E30051",

"18-280222-E30254",

"18-280222-E30417",

"18-280222-E30257",

"18-280222-E30227"]

value = "18-030322-E30808"


# for value in qrs:
#
#         print(requests.delete("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + value))

for qr in qrs:

        test = requests.get("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + qr)

        dom_record = json.loads(test.text)

        print(dom_record)
