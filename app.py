from flask import Flask, json, request
from flask_cors import CORS, cross_origin
from binascii import a2b_base64
import urllib
import qrtools
import pyqrcode
from pyzbar.pyzbar import decode
from PIL import Image
import json
import sys
import zlib
import base45
import cbor2
from cose.messages import CoseMessage
import base64


UPLOADED_IMAGE_NAME = "image.jpg"
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def index():
    return "Hello World"



@app.route('/verify_qr', methods=['POST'])
@cross_origin()
def verify_qr():
    data = request.get_json() 
    response = urllib.request.urlopen(data['image'])
    with open(UPLOADED_IMAGE_NAME, 'wb') as f:
        f.write(response.file.read())
    foo = Image.open(UPLOADED_IMAGE_NAME)
    foo = foo.resize((256,256),Image.ANTIALIAS)
    
    print(foo.size)
    data = decode(foo)
    
    if len(data) > 0:
        raw_str = str(data[0].data)
        raw_str = raw_str.replace("b'", "").replace("'","")

        payload = raw_str[4:]
        decoded = base45.b45decode(payload)

        decompressed = zlib.decompress(decoded)
        
        cose = CoseMessage.decode(decompressed)
        grennpass_json = json.dumps(cbor2.loads(cose.payload), indent=2)


        #image to send back
        qr = pyqrcode.create(raw_str)
        qr.png("clean_greenpass.png", scale=2)

        encoded = base64.b64encode(open("clean_greenpass.png", "rb").read())
        encoded = 'data:image/png;base64,{}'.format(str(encoded)[2:-1])
        
       
        print("Grennpass decodificato! Invio Informazioni")
        return ({"greenpass_info" : grennpass_json, "greenpass_image":encoded})
    else:
        print("errore")
        return {"error":"Invalid cant extract qrcode from this image"}

if __name__ == "__main__":        
    app.run()