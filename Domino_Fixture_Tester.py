import requests
import json
import time

qrs = ["18-280222-E30030",

"18-280222-E30780",

"18-280222-E30276",

"18-280222-E30037",

"18-280222-E30055",

"18-280222-E30354",

"18-280222-E30714",

"18-280222-E30079",

"18-280222-E30370",

"18-280222-E30227"]

value = "18-280222-E30026"

gotten_qrs = []
#
# for value in qrs:
#
#         print(requests.delete("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + value))_

# for qr in qrs:
        # while True:
test = requests.get("https://trksbxmanuf.azure-api.net/black-domino/v2/domino-test?qrcode=" + value)

dom_record = json.loads(test.text)
# if dom_record != []:
#         gotten_qrs.append(dom_record[0]['qrcode'])
#         print(gotten_qrs)
print(dom_record[0]['qrcode'][0])
        # time.sleep(30)


# ========================= 18-280222-E30030 Passes =========================
# ========================= 18-280222-E30780 Passes =========================
# ========================= 18-280222-E30276 Passes =========================
# ========================= 18-280222-E30037 Passes =========================
# ========================= 18-280222-E30055 Passes =========================
# ========================= 18-280222-E30354 Passes =========================
# ========================= 18-280222-E30714 Passes =========================
# ========================= 18-280222-E30079 Passes =========================
# ========================= 18-280222-E30370 Passes =========================
