import cognitive_face as CF

KEY = '875ba7bdf8df47da919b047314b97ca9'  # Replace with a valid subscription key (keeping the quotes in place).
CF.Key.set(KEY)

BASE_URL = 'https://westus.api.cognitive.microsoft.com/face/v1.0/'  # Replace with your regional Base URL
CF.BaseUrl.set(BASE_URL)

# You can use this example JPG or replace the URL below with your own URL to a JPEG image.
img_url = 'https://scontent-sjc3-1.cdninstagram.com/vp/e578e45b2c00d026fc363ee2d44bedb1/5BB817E8/t51.2885-19/s150x150/34611418_280277852713481_1217678594839412736_n.jpg'
faces = CF.face.detect(img_url)
print(faces)