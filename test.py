import requests
import json

params = {
	'returnFaceId': 'true',
	'returnFaceLandmarks': 'false',
	'returnFaceAttributes': 'age,gender,smile',
}

headers = {
	'Content-Type': 'application/json',
	'Ocp-Apim-Subscription-Key': '875ba7bdf8df47da919b047314b97ca9',
}

URL = 'https://westus.api.cognitive.microsoft.com/face/v1.0/detect'
# param_string = '?{0}'.format(params)
# URL = URL + param_string
# print(URL)

data = {'url': 'https://scontent-sjc3-1.cdninstagram.com/vp/e578e45b2c00d026fc363ee2d44bedb1/5BB817E8/t51.2885-19/s150x150/34611418_280277852713481_1217678594839412736_n.jpg',}

response = requests.post(URL, headers = headers, json = data)

response_json = json.loads(response.content.decode('utf-8'))
print(json.dumps(response_json, indent = 2, sort_keys = True))



