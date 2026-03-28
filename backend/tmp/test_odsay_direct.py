import os, requests
from dotenv import load_dotenv

load_dotenv("c:\\Users\\rkgka\\OneDrive\\바탕 화면\\3Team_FlaskPJ_test\\backend\\.env")
ODSAY_KEY = os.getenv("ODSAY_API_KEY")

odsay_url = "https://api.odsay.com/v1/api/searchPubTransPathT"
odsay_params = {
    "apiKey": ODSAY_KEY,
    "SX": "127.0016", "SY": "37.2655", # Suwon station (roughly)
    "EX": "127.0286", "EY": "37.2635", # Suwon city hall
    "SearchPathType": 0
}

res = requests.get(odsay_url, params=odsay_params, timeout=10)
print("ODsay direct response:")
print(res.json())
