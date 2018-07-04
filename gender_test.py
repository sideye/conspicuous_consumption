import gender_guesser.detector as gender
import requests
from bs4 import BeautifulSoup as soup
import json

detector = gender.Detector()
print("Maximillian", detector.get_gender("Maximillian"))
print("Maximilian Mueller", detector.get_gender("Maximilian Mueller"))
print("Alan", detector.get_gender("Alan"))


def detect_name(username): 
	url = "https://apinsta.herokuapp.com/u/" + username
	r = requests.get(url)
	profile = json.loads(r.text)
	print(r.text)

detect_name("alankliang")