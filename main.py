import requests, lxml, re, json
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask('app')
CORS(app)

__version__ = 1

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
}

@app.route('/')
def main():
  return jsonify({
    'version' : __version__
  })

@app.route('/google/<text>&limit=<limit>')
def google(text, limit):
  result = []
  params = {"q": text, "tbm": "isch", "hl": "en", "ijn": "0"}

  response = requests.get("https://www.google.com/search", params=params, headers=headers)
  soup = BeautifulSoup(response.text, 'lxml')

  tags = soup.select('script')
  
  images_data = ''.join(re.findall(r"AF_initDataCallback\(([^<]+)\);", str(tags))) #해당하는 글자를 찾는다(findall)

  images_data = json.dumps(images_data) #json에 해당하는 문자열 반환
  images_data = json.loads(images_data) #반환된 문자열을 json타입으로 변환

  google_image_data = re.findall(r'\[\"GRID_STATE0\",null,\[\[1,\[0,\".*?\",(.*),\"All\",', images_data)
  
  # 문자열 바꾸기(sub)
  images_thumbnails = re.sub(r'\[\"(https\:\/\/encrypted-tbn0\.gstatic\.com\/images\?.*?)\",\d+,\d+\]', '', str(google_image_data)) #이미지 링크 베이스
  google_images = re.findall(r"(?:'|,),\[\"(https:|http.*?)\",\d+,\d+\]", images_thumbnails) #유효한 이미지 링크 찾기

  for index, image in enumerate(google_images): #튜플
    img = bytes(image,'ascii').decode('unicode-escape')
    img = bytes(img, 'ascii').decode('unicode-escape')

    if limit:
      if index < int(limit):
        result.append(img)
      else:
        break

    else:
      result.append(img)

  result = app.response_class(response=json.dumps(result), mimetype="application/json")
  return result
  

app.run(host='0.0.0.0', port=8080)
