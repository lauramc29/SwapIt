
import requests
import json

url = "https://api.apilayer.com/bad_words?censor_character=*"

payload = "asdhga shit".encode("utf-8")
headers= {
  "apikey": "ezdJ8Qt7qVLADpnpaieeAeGaLw7itA8I"
}

response = requests.request("POST", url, headers=headers, data = payload)

status_code = response.status_code
result = response.text
resultjs = json.loads(result)
finalcontent = resultjs["censored_content"]
print(finalcontent)