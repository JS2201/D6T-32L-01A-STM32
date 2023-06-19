# -*- coding: utf-8 -*-
"""
Created on Fri May 12 10:16:08 2023

@author: Jason Shaji
"""
### Description: Video-based GUI. Displays images with a definite time delay. 
### Edit lines 256 and 302 to change the time delay in milliseconds.

from tkinter import *
import serial
import time
import struct
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import pandas as pd
import matplotlib.pyplot as plt
import threading
import statistics

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


data = 0
a = 0
#global cap_flag
#start = time.time()

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
        #plt.imshow(img_scaled, cmap= 'gray', vmin = 0, vmax = 255)
        '''f_reshape= open('D:\Jason\STM Files\img_reshape3.csv', 'r+')
        np.savetxt(f_reshape, img_np_array2, delimiter= ',')
        f_reshape.close()
        f_scaled= open('D:\Jason\STM Files\img_scaled3.csv', 'r+')
        np.savetxt(f_scaled, img_scaled, delimiter= ',')
        f_scaled.close()'''
        print(img_np_array2)
        #img_gen = Image.fromarray(img_scaled)
        #img_gen.save('D:\Jason\STM Files\D6T_temp_image.png')
        return img_scaled, max(l2), min(l2), img_np_rC, img_np_bC, avg_val
        #else:
    #return img_gen

def send1():
    #ser.open()
    try:
        ser.write(b'1')
        #t1.start()
        #send2()
    except serial.serialutil.PortNotOpenError:
        ser.open()
        ser.write(b'1')
        #t1.start()
        #send2()

def send2():
        ser.write(b'2') 
        #t2.start()
        c, mt, mit, rC, bC, avg = getnshow_SensorValues()
        cord = np.where(c == np.amax(c))
        print(np.ndim(cord))
        print(cord)
        if len(cord[0]) > 1:      ###handling for multiple coordinates
            fcordx, fcordy = cord[0][-1], cord[-1][-1]
        else:
            fcordx, fcordy = cord
        print(fcordx, fcordy)
        s = "*Max. Temp=" + str(mt) + " degC"
        var = mt - mit
        print(mt)
        print(mit)
        print("Variation = ", var)
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
        img_fname = "D:\\Jason\\Python Files\\FMTMS_Trap_Readings5\\" + str(avg) + ".png"
        plt.savefig(img_fname)
        lbl2.config(image= img2)
        lbl2.image = img2
        lbl2.update_idletasks()
        lbl3.config(text= s)
        with open("TOFT Chamber- 30th May.txt", "a") as file1:
            file1.write(time.asctime().split(" ")[3] + "," + str(avg) + "\n")
        
        ###Contouring
        '''img3 = cv2.imread(img_fname)
        print(img3.shape)
        b, g, r = cv2.split(img_sliced)
        img_sliced = np.zeros([80, 80, 3], dtype= np.uint8)
        for i in range(0, 80):
            for j in range(0, 80):
                img_sliced[i, j] = [img_gen[i + 120, j + 120, 0], 0, img_gen[i + 120, j + 120, 2]]
        img_sliced_gen = Image.fromarray(img_sliced)
        #plt.imshow(img_sliced_gen)
        img_gray = cv2.cvtColor(img_sliced_gen, cv2.COLOR_BGR2GRAY)
        #plt.hist(img_gray.ravel(), bins= 256, range=(0, 255))
        #img_sliced = img_gray[100:700, 100:700]
        #cv2.imshow('image', img_gray)
        print(np.amax(img_gray))
        print(np.amin(img_gray))
        thresh_value = (np.amax(img_gray) - np.amin(img_gray))//2
        ret, thresh = cv2.threshold(img_gray, np.amin(img_gray) + thresh_value, 255, cv2.THRESH_BINARY)
        cv2.imshow('binary', thresh)
        contours, hierarchy = cv2.findContours(image = thresh, mode = cv2.RETR_TREE, method = cv2.CHAIN_APPROX_NONE)
        #print(hierarchy)
        #print(contours)
        a = np.array(contours)
        #print(a[0, 2, 0, 0]) 
        #print(a.shape)
        #ct_coord = []
        print(len(a[0]))
        for c in range(len(a[0])):
            if a[0, c, 0, 0] == 0 or a[0, c, 0, 0] == thresh.shape[0] - 1:
                continue
            else:
                ct_coord.append(a[0, c, 0])
        print("Surface contour length: ", len(ct_coord))
        #print(len(ct_coord))
        img_copy = img_sliced.copy()
        cv2.drawContours(image = img_copy, contours = contours, contourIdx = -1, color = (0,255,255), thickness = 2, lineType = cv2.LINE_AA)
        cv2.imshow('edges', img_copy)
        #print(thresh.shape)
        #print(ct_coord)
        #print(img_sliced)
        #rgb_pixv = []
        #temp = []
        rgb_pixv1 = []
        temp1 = []
        zscore1 = []
        interval1 = []
        #for d in range(0, len(ct_coord)):
        #    rgb_pixv.append(img_sliced[ct_coord[d][0], ct_coord[d][1]][2])
        #    temp.append(round(((rgb_pixv[d]*150)/255),2))                       ##Boundary
            
        for i in range(0, thresh.shape[0], 1):
            for j in range(0, thresh.shape[1], 1):
                if (thresh[i, j] == 255):
                    rgb_pixv1.append(img_sliced[i, j][2])
                    temp1.append(round(((img_sliced[i, j][2]*150)/255),2))      ##Area 
        #print(temp1)
        #print(temp)
        #print(rgb_pixv)

        #sum3 = 0
        #sum4 = 0
        #for m in range(0, img_sliced.shape[0]):
        #    for n in range(0, img_sliced.shape[0]):
        #        sum3 += img_sliced[m, n][0]
        #        sum4 += img_sliced[m, n][2]
        #print("Mean Temperature of Contour (Boundary)= ", statistics.mean(temp))
        #print("Avg. of blue pixels= ", sum3//6400)
        #print("Avg. of red pixels= ", sum4//6400)
        print("Max. Temperature of sliced image: ", max(temp1))
        print("Min. Temperature of sliced image: ", min(temp1))
        print("Mean Temperature of Contour (Area)= ", statistics.mean(temp1))
        m = statistics.mean(temp1)
        sd = statistics.stdev(temp1)
        for p in range(0, len(temp1)):
            zscore1.append((temp1[p] - m) / sd)
            if zscore1[p] <= 1 and zscore1[p] >= -1:
                interval1.append(temp1[p])
        print(len(interval1))
        print("Avg. temperature using RSD=  ", statistics.mean(interval1))
        #plt.hist(interval1, 200)
        #lbl4.config(image= img_copy)
        #lbl4.image = img_copy
        #lbl4.update_idletasks()
        cv2.waitKey(50)'''

def eval_all_flags():
    print("In function")
    if cap_flag:
        send1()
        #print("1")
        send2()
        #print("2")
    #time.sleep(500)
    root.after(30000, eval_all_flags)     ##50

def start_cap():
    try:
        ser.close()
        ser.open()
        global cap_flag
        cap_flag = True
    except serial.serialutil.SerialException:
        ser.close()
        ser.open()
        #global cap_flag
        print("Exception")
        cap_flag = True

def stop_cap():
    ser.close()
    print("Stop")
    global cap_flag
    cap_flag = False
    #cv2.destroyAllWindows()
    #root.destroy()


root= Tk()
root.geometry("700x500")
cap_flag = True
root.title("D6T MEMS Thermal Sensor")
lbl1= Label(root, text= "D6T MEMS Thermal Sensor", height= 3, width= 24)
lbl1.grid(row= 0, column= 0)
#image
#opening images
#image1= ImageTk.PhotoImage(Image.open('D:\Jason\STM Files\D6T_temp_image.png'))
lbl2 = Label(root)   #packing image into the window
lbl2.grid(row= 1, column= 0)
lbl3 = Label(root)   #temperature text
lbl3.grid(row= 2, column= 0)
#lbl4 = Label(root)
#cap_flag = True
################
b1 = Button(root, text = "Start Capture", command= start_cap).grid(row= 3, column= 0, sticky= W)
b2 = Button(root, text = "Stop Capture", command= stop_cap).grid(row= 3, column= 0, sticky= E)
#b3 = Button(root, text = "Display Images", command= eval_all_flags).grid(row= 4, column= 0)
#b4 = Button(root, text = "Show_Image", command= send2).place(x= 300, y= 450)
#b1 = Button(root, text = "Capture" ).place(x= 400, y= 100)

root.after(30000, eval_all_flags)   ###printing one img at a time
#root.bind("<Escape>", stop_cap)
root.mainloop()
    