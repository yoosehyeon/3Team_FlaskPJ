import os, requests
from urllib.parse import unquote

ODSAY_KEY = "ezHyHNB1973AQ+4Zobzd0g"

odsay_url = f"https://api.odsay.com/v1/api/searchPubTransPathT?SX=127.0016&SY=37.2655&EX=127.0286&EY=37.2635&SearchPathType=0&apiKey={ODSAY_KEY}"

res = requests.get(odsay_url, timeout=10)
print("ODsay unencoded url response:")
print(res.json())

from urllib.parse import quote
encoded_key = quote(ODSAY_KEY)
odsay_url_enc = f"https://api.odsay.com/v1/api/searchPubTransPathT?SX=127.0016&SY=37.2655&EX=127.0286&EY=37.2635&SearchPathType=0&apiKey={encoded_key}"
res_enc = requests.get(odsay_url_enc, timeout=10)
print("ODsay encoded url response:")
print(res_enc.json())
