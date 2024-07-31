#!/usr/bin/env python3

# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
Newtworking Application

Make Cozmo communicate with other Cozmo robots

'''

import cozmo
import socket
import errno
import qrcode
from socket import error as socket_error
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
from PIL import Image
#need to get movement info
from cozmo.util import degrees, distance_mm, speed_mmps

#NOTE: in a terminal, open python
'''
import socket
s = socket.socket()
s.connect(('10.0.1.10', 5000))
s.sendall(b'message') or s.recv(4096)

'''
def parseMessage(message):
    l = list(message.split(";"))
    newl = []
    if len(l)> 0:
        for i in l:
            if i.isdigit() == True:
                i = int(i)
            newl.append(i)
        return newl
    else:
        l = list(message.split("_"))
        for i in l:
            if i.isdigit() == True:
                i = int(i)
            newl.append(i)
        return newl


def QRPickUp(robot):
    new_im = robot.world.wait_for(cozmo.world.EvtNewCameraImage)
    new_im.image.raw_image.show()

        #save the raw img as a bmp
    img_latest = robot.world.latest_image.raw_image
    img_convert = img_latest.convert('L')
    img_convert.save('QRPic.bmp')

        #save the img data as a png
    imageName = "Card.png"
    img = Image.open('QRPic.bmp')
    width, height = img.size
    new_img = img.resize((width, height))
    new_img.save(imageName, 'png')

    decodedImage = decode(Image.open(imageName), symbols = [ZBarSymbol.QRCODE])
    #print(decodedImage)
    if len(decodedImage) > 0:
        codeData = decodedImage[0]
        myData = codeData.data
        myString = myData.decode('ASCII')
        return parseMessage(myString)
    else:
        print('I could not find the data.')

def cozmo_program(robot: cozmo.robot.Robot):
    '''try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket_error as msg:
        robot.say_text("socket failed" + msg).wait_for_completed()
    ip = "10.0.1.10" # always this ip
    port = 5000 # always this for port
    
    try:
        s.connect((ip, port))
    except socket_error as msg:
        robot.say_text("socket failed to bind").wait_for_completed()'''
    cont = True
    
    robot.say_text("ready").wait_for_completed()   

    robot.camera.image_stream_enabled = True
    robot.set_head_angle(degrees(3)).wait_for_completed()

    #SET COZMO's NAME
    myName = 'Zeek'

    #robot.camera.image_stream_enabled = True 
    count = 0 
    test = []
    tot = 0
    net = []
    hand = []
    #parse the message to turn and ints into ints
    while count < 2:

        msg = QRPickUp(robot)
        robot.say_text("My card is" + str(msg[0]) + 'of' + str(msg[1])).wait_for_completed()

        if msg[0] == 'Jack':
            msg[0] = 10
        elif msg[0] == 'Queen':
            msg[0] = 10
        elif msg[0] == 'King':
            msg[0] = 10
        elif msg[0] == 'Ace':
            msg[0] = 11
    
        print(msg)
        test.append(msg[0])
        tot = sum(test)
        #add data to hand
        hand.append(msg)
        print(test)
        print(tot)
        robot.turn_in_place(cozmo.util.degrees(180)).wait_for_completed()

        count += 1
    if tot == 21:
        robot.say_text('Thats a BlackJack yay').wait_for_completed()
        robot.turn_in_place(cozmo.util.degrees(360)).wait_for_completed()
    elif tot < 15:
        robot.say_text('Hit me I only have ' + str(tot)).wait_for_completed()
        robot.anim_triggers(cozmo.anim.Triggers.HiccupRobotOnFace).wait_for_completed()
        #robot.set_lift_height(0.0).wait_for_completed()  
    elif tot >= 16:
        robot.say_text("I have " + str(tot) + "so I will stay and pray.").wait_for_completed()
        robot.turn_in_place(cozmo.util.degrees(90)).wait_for_completed()

cozmo.run_program(cozmo_program, use_viewer=True, force_viewer_on_top=True)
