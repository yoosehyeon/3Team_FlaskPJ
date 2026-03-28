import requests

ODSAY_KEY = "ezHyHNB1973AQ+4Zobzd0g"
odsay_url = "https://api.odsay.com/v1/api/searchPubTransPathT"
odsay_params = {
    "apiKey": ODSAY_KEY,
    "SX": "127.0016", "SY": "37.2655", # Suwon station (roughly)
    "EX": "127.0286", "EY": "37.2635", # Suwon city hall
    "SearchPathType": 0
}

# Test with Referer matched to the registered URI
headers = {
    "Referer": "https://test1234112.netlify.app"
}

res = requests.get(odsay_url, params=odsay_params, headers=headers, timeout=10)
print("Response with https://test1234112.netlify.app Referer:")
print(res.json())

# Test with another Referer
headers2 = {
    "Referer": "http://127.0.0.1:5000"
}
res2 = requests.get(odsay_url, params=odsay_params, headers=headers2, timeout=10)
print("Response with http://127.0.0.1:5000 Referer:")
print(res2.json())
