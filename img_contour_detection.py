# -*- coding: utf-8 -*-
"""
Created on Tue May  2 12:11:57 2023

@author: Jason Shaji
"""
### Description: Image-contouring code. 
### Images must be saved in directories for the code to work.

import cv2
import numpy as np
import matplotlib.pyplot as plt
import statistics

img = cv2.imread('D:\\Jason\\Python Files\\152.7.png')
print(img.shape)
img_sliced = img[104:184, 176:256]        ### [y-axis, x-axis]
#b, g, r = cv2.split(img_sliced)
img_gray = cv2.cvtColor(img_sliced, cv2.COLOR_BGR2GRAY)
#plt.hist(img_gray.ravel(), bins= 256, range=(0, 255))
#img_sliced = img_gray[100:700, 100:700]
#histb = cv2.calcHist([img_sliced], [0], None, [256], [0, 256])
#histg = cv2.calcHist([img_sliced], [1], None, [256], [0, 256])
#histr = cv2.calcHist([img_sliced], [2], None, [256], [0, 256])
#plt.plot(histg)
#plt.plot(histr)
print(np.amax(img_gray))
print(np.amin(img_gray))
thresh_value = (np.amax(img_gray) - np.amin(img_gray))//2
cv2.imshow('image', img_gray)
ret, thresh = cv2.threshold(img_gray, np.amin(img_gray) + thresh_value, 255, cv2.THRESH_BINARY)    ###45
cv2.imshow('binary', thresh)
contours, hierarchy = cv2.findContours(image = thresh, mode = cv2.RETR_TREE, method = cv2.CHAIN_APPROX_NONE)
#print(hierarchy)
#print(contours)
a = np.array(contours)
#print(a[0, 2, 0, 0]) 
#print(a.shape)
#ct_coord = []
print(a.shape)
'''for c in range(len(a[0])):
    if a[0, c, 0, 0] == 0 or a[0, c, 0, 0] == thresh.shape[0] - 1:
        continue
    else:
        ct_coord.append(a[0, c, 0])
print("Surface contour length: ", len(ct_coord))
#print(len(ct_coord))'''
if len(a.shape) > 1:
    img_copy = img_sliced.copy()
    cv2.drawContours(image = img_copy, contours = contours, contourIdx = -1, color = (0,255,255), thickness = 2, lineType = cv2.LINE_AA)
    cv2.imshow('edges', img_copy)
    print(thresh.shape)
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
    print(temp1)
    #print(temp)
    #print(rgb_pixv)
    
    sum3 = 0
    sum4 = 0
    for m in range(0, img_sliced.shape[0]):
        for n in range(0, img_sliced.shape[0]):
            sum3 += img_sliced[m, n][0]
            sum4 += img_sliced[m, n][2]
    print("Mean Temperature of Contour (Area)= ", statistics.mean(temp1))
    #print("Mean Temperature of Contour (Boundary)= ", statistics.mean(temp))
    #print("Avg. of blue pixels= ", sum3//6400)
    #print("Avg. of red pixels= ", sum4//6400)
    print(max(temp1))
    print(min(temp1))
    m = statistics.mean(temp1)
    sd = statistics.stdev(temp1)
    for p in range(0, len(temp1)):
        zscore1.append((temp1[p] - m) / sd)
        if zscore1[p] <= 1 and zscore1[p] >= -1:
            interval1.append(temp1[p])
    print(len(interval1))
    print("Avg. temperature using RSD=  ", statistics.mean(interval1))
    plt.hist(interval1, 200)
else:
    print("Contour cannot be formed!!!")
cv2.waitKey(0)
cv2.destroyAllWindows()