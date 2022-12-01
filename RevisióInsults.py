
import requests
import json 

def comprovacio_insults(text):
  url = "https://api.apilayer.com/bad_words?censor_character=*"

  payload = text.encode("utf-8")
  headers= {
    "apikey": "ezdJ8Qt7qVLADpnpaieeAeGaLw7itA8I"
  }

  response = requests.request("POST", url, headers=headers, data = payload)

  status_code = response.status_code
  result = response.text
  resultjs = json.loads(result)
  finalcontent = resultjs["censored_content"]
  return(finalcontent)
print(comprovacio_insults("You're an asshole"))
