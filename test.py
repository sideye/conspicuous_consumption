import requests
import json

# Get started guide: https://docs.microsoft.com/en-us/azure/cognitive-services/face/quickstarts/python
# Documentation: https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395236

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

data = {'url': 'https://images.wbbjtv.com/wp-content/uploads/2016/03/tree.jpg',}

response = requests.post(URL, params = params, headers = headers, json = data)

response_json = json.loads(response.content.decode('utf-8'))
print(response_json)
#print(response_json[0]["faceAttributes"]["age"])