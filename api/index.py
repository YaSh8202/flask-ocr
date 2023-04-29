from flask import Flask, request, jsonify
import cv2
import pytesseract
from pytesseract import Output
import PIL.Image
import urllib.request
import numpy

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'


myconfig=r"--psm 11 --oem 3"

def ocr_core(url):
    img = cv2.imdecode(numpy.array(bytearray(urllib.request.urlopen(url).read()), dtype=numpy.uint8), -1)
    data=pytesseract.image_to_data(img, config=myconfig, output_type=Output.DICT)

    amount_of_boxes=len(data['text'])
    for i in range(amount_of_boxes):
        if float(data['conf'][i])>50:  #confidence over 80, only then apply boxes
            (x,y,height,width)=(data['left'][i],data['top'][i], data['height'][i], data['width'][i])
            img=cv2.rectangle(img, (x,y), (x+width,y+height), (0,255,0),2)
            img=cv2.putText(img, data['text'][i], (x,y+height+20), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0,255,0),2,cv2.LINE_AA)
    cv2.imwrite("result.png", img)
    text=pytesseract.image_to_string(PIL.Image.open("result.png"),config=myconfig)
    return text

@app.route('/ocr', methods=['POST'])
def ocr():
    url = request.json['url']
    result = ocr_core(url)
    return jsonify({'result': result})