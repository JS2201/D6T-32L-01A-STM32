
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 11:32:37 2023

@author: Jason Shaji
"""
### Description: Image-based GUI. Can capture and show images with the help of user input.

from tkinter import *
import serial
import time
import struct
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import pandas as pd
import matplotlib.pyplot as plt

ser = serial.Serial()
#ser.port = "/dev/ttyUSB0"
ser.port = "COM9"
#ser.port = "/dev/ttyS2"
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
ser.timeout = None           #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardwar'e (DSR/DTR) flow control
ser.writeTimeout = 10000     #timeout for write

#time.sleep(2)
data = 0
a = 0

def getnshow_SensorValues():
    #ser.open()
    #time.sleep(1)
    #ser.write(b'1')
    data= ser.read(1024*4)
    #print(data)
    data_hex= data.hex()
    #print(len(data_hex)/8)
    l1= []
    l2= []
    c=8
    #if len(data_hex) == 8*1024:
    for d in range(0, len(data_hex),8):     #Length check while debugging
          l1.append(data_hex[d:c])
          c=c+8
    print(len(l1))
    if len(l1) < 1024:
        print("Invalid packet size!!!!")
    else:
        for b in range(0,len(l1)):
            a = round(struct.unpack('f', bytes.fromhex(l1[b]))[0], 2)
            #a = float.fromhex(l1[b])
            #print(a)
            l2.append(a)
        print("Length of l2: ", len(l2))
        avg_val = round(sum(l2)/len(l2), 2)
        #print(l2)
        img_np_array = np.array(l2)
        img_np_array2 = img_np_array.reshape((32,32))
        img_scaled = img_np_array2 * (255/200)
        img_redComponent = []
        img_blueComponent = []
        for k in range(0, len(l2)):
            img_redComponent.append(int(l2[k] * (255/200)))
            img_blueComponent.append(255 - img_redComponent[k])
        print("Red")
        print(img_redComponent)
        print("Blue")
        print(img_blueComponent)
        img_np_rC = np.array(img_redComponent)
        img_np_bC = np.array(img_blueComponent)
        img_np_rC = img_np_rC.reshape((32,32))
        img_np_bC = img_np_bC.reshape((32,32))
        plt.imshow(img_scaled, cmap= 'gray', vmin = 0, vmax = 255)
        '''f_reshape= open('D:\Jason\STM Files\img_reshape3.csv', 'r+')
        np.savetxt(f_reshape, img_np_array2, delimiter= ',')
        f_reshape.close()
        f_scaled= open('D:\Jason\STM Files\img_scaled3.csv', 'r+')
        np.savetxt(f_scaled, img_scaled, delimiter= ',')
        f_scaled.close()'''
        print(img_np_array2)
        #img_gen = Image.fromarray(img_scaled)
        #img_gen.save('D:\Jason\STM Files\D6T_temp_image.png')
        return img_scaled, max(l2), img_np_rC, img_np_bC, avg_val
        #else:
    #return img_gen

def send1():
    #ser.open()
    try:
        ser.write(b'1')
    except serial.serialutil.PortNotOpenError:
        ser.open()
        ser.write(b'1')

def send2():
    ser.write(b'2') 
    c, mt, rC, bC, avg = getnshow_SensorValues()
    cord = np.where(c == np.amax(c))
    print(np.ndim(cord))
    print(cord)
    if len(cord[0]) > 1:      ###handling for multiple coordinates
        fcordx, fcordy = cord[0][-1], cord[-1][-1]
    else:
        fcordx, fcordy = cord
    print(fcordx, fcordy)
    s = "*Max. Temp=" + str(mt) + " degC"
    #s = "Max. Temp= " + str(c[xcord][ycord])
    #img_s = Image.fromarray(c)
    #img_s.save('D:\\Jason\\Python Files\\D6T_temp_image.png')
    #img_o = Image.open(img_s)
    #t1 = ImageDraw.Draw(img_o)
    #t1.text((xcord,ycord), s, fill= (255, 0, 0))
    #img_o.show()
    #img2 = ImageTk.PhotoImage(file= "D:\Jason\STM Files\D6T_temp_image1.png")
    #lbl2.config(image= img2)
    #lbl2.image = img2
    
    
    img_zero = np.zeros([32,32,3], dtype= np.uint8)
    for i in range(0, 32):
        for j in range(0, 32):
            img_zero[i, j] = [rC[i, j], 0, bC[i, j]]
    img_gen = Image.fromarray(img_zero)
    #plt.imshow(img_gen)
    #t1 = ImageDraw.Draw(img_gen)
    #t1.text((cord[0], cord[1]), s)
    factor = 10
    img_gen= img_gen.resize((32*factor,32*factor))
    t1 = ImageDraw.Draw(img_gen)
    t1.text((fcordx*factor, fcordy*factor), s)
    img2 = ImageTk.PhotoImage(image= img_gen)
    plt.imshow(img_gen)
    img_fname = str(avg) + ".png"
    plt.savefig(img_fname)
    lbl2.config(image= img2)
    lbl2.image = img2
    lbl3.config(text= s)
    #ser.close()

def ser_open():
    try:
        ser.open()
    except serial.serialutil.SerialException:
        ser.close()
        ser.open()

def ser_close():
    ser.close()

root= Tk()
root.geometry("500x500")
root.title("D6T MEMS Thermal Sensor")
lbl1= Label(root, text= "D6T MEMS Thermal Sensor", height= 3, width= 24)
#image
#opening images
#image1= ImageTk.PhotoImage(Image.open('D:\Jason\STM Files\D6T_temp_image.png'))
lbl2 = Label(root)   #packing image into the window
lbl3 = Label(root)
################
b1 = Button(root, text = "Serial_open", command= ser_open).place(x= 100, y= 400)
b2 = Button(root, text = "Serial_close", command= ser_close).place(x= 300, y= 400)
b3 = Button(root, text = "Capture_Image", command= send1).place(x= 100, y= 450)
b4 = Button(root, text = "Show_Image", command= send2).place(x= 300, y= 450)
#b1 = Button(root, text = "Capture" ).place(x= 400, y= 100)
lbl1.pack()
lbl2.pack()
lbl3.pack()
root.mainloop()
    