import gender_guesser.detector as gender
import requests
from bs4 import BeautifulSoup 
import json
import re

detector = gender.Detector()
print("Maximillian", detector.get_gender("Maximillian"))
print("Maximilian Mueller", detector.get_gender("Maximilian Mueller"))
print("Alan", detector.get_gender("Alan"))


print()
# Testing for user profile accessor and gender analyzer. 
def detect_name(username): 
	url = "https://apinsta.herokuapp.com/u/" + username
	r = requests.get(url)
	profile = json.loads(r.text)
	full_name = profile["graphql"]["user"]["full_name"]
	first_name = re.compile('\w+').findall(full_name)[0]
	gender = detector.get_gender(first_name)
	return gender

#print(detect_name("alankliang"))




r = requests.get('https://www.instagram.com/alankliang/')
soup = BeautifulSoup(r.content)
scripts = soup.find_all('script', type="text/javascript", text=re.compile('window._sharedData'))
stringified_json = scripts[0].get_text().replace('window._sharedData = ', '')[:-1]

json.loads(stringified_json)['entry_data']['ProfilePage'][0]