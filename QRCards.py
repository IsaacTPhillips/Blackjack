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

spot = 0 
suit = ['Heart', 'Spade', 'Diamond', 'Clubs']
faces = ['Jack', 'Queen', 'King', 'Ace']
count = 0
while spot < 4: 
    while count < 4:
        img = qrcode.make(faces[count] + ";" + suit[spot])
        img.save(faces[count]+ suit[spot] +'.png')
        count += 1
    count = 0
    spot += 1
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