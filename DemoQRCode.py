#import the QRCode creater library: https://pypi.org/project/qrcode/
#pip install qrcode...this one is fine
import qrcode
#pip install pyqrcode...here is a different option
import pyqrcode
#import the QRCode reader libraries: https://pypi.org/project/pyzbar/
#pip install pyzbar
#pip install PIL (this you probably already have)

from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
from PIL import Image


myText = 'Let us create a QR code'
count = 2
img = qrcode.make(myText)
img.save('DemoQRCode.png')

decodedImage = decode(Image.open('DemoQRCode.png'), symbols = [ZBarSymbol.QRCODE])
print(decodedImage)
if len(decodedImage) > 0:
    codeData = decodedImage[0]
    myData = codeData.data
    myString = myData.decode('ASCII')
    print(myString)
else:
    print('I could not find the data.')

'''network stuff: 
import socket
s = socket.socket()
s.sendall(b'hello')
s.recv(4090)'''