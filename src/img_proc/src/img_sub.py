#!/usr/bin/env python
#coding:utf-8

from __future__ import print_function
import sys
import numpy as np
#from std_msgs.msg
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge,CvBridgeError
import cv2

def watershed(img_gray,img_source):
    img_shape = np.zeros_like(img_gray);

    ret,img_thresh = cv2.threshold(img_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    kernel = np.ones((3,3),np.uint8)

    img_opening = cv2.morphologyEx(img_thresh,cv2.MORPH_OPEN,kernel,iterations=2)

    sure_bg = cv2.dilate(img_opening,kernel,iterations=3)

    dist_transform = cv2.distanceTransform(img_opening,cv2.DIST_L2,5)
    ret,sure_fg = cv2.threshold(dist_transform,0.5*dist_transform.max(),255,0)
    sure_fg = np.uint8(sure_fg)

    unknown = cv2.subtract(sure_bg,sure_fg)

    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown ==255]=0
    markers = cv2.watershed(img_source,markers)
    img_shape[markers == -1]= 255

    return img_shape

def perspective_transformation(img,img_source):
    contours,ret = cv2.findContours(img,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]

    epsilon = 0.1*cv2.arcLength(cnt,True)
    approx = cv2.approxPolyDP(cnt,epsilon,True)

    if len(approx) != 4:
        pts1 = np.float32([[0,0],[0,0],[0,0],[0,0]])
    else :
        mean = approx.mean(axis=2).squeeze()
        idx_sort = mean.argsort()
        sub = approx[idx_sort[1]] - approx[idx_sort[2]]

        if sub[0][0] > 0:
            a = idx_sort[1]
            b = idx_sort[2]
        else :
            a = idx_sort[2]
            b = idx_sort[1]
            
        pts1 = np.float32([approx[idx_sort[0]],approx[a],approx[b],approx[idx_sort[3]]])

        pts2 = np.float32([[0,0],[500,0],[0,500],[500,500]])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        img_warp = cv2.warpPerspective(img_source,M,(500,500))

        return img_warp


def clache(img):
    img_yuv = cv2.cvtColor(img,cv2.COLOR_BGR2YUV)
    img_clahe = img_yuv.copy()
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize = (8,8))
    img_clahe[:,:,0] = clahe.apply(img_clahe[:,:,0])
    img_clahe = cv2.cvtColor(img_clahe,cv2.COLOR_YUV2BGR)
    return img_clahe


class libbot(object):
    def __init__(self):
        self.bridge = CvBridge()
        self.img_pub = rospy.Publisher("image_thres",Image,queue_size = 5) 
        self.img_sub = rospy.Subscriber("/image_raw",Image,self.callback)
        

    def callback(self,data):
        img = self.bridge.imgmsg_to_cv2(data,"bgr8")
        
        img_gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img_watershed = watershed(img_gray,img)
        img_warp = perspective_transformation(img_watershed,img)
        img_clahe = clache(img_warp)
        img_gray2 = cv2.cvtColor(img_clache, cv2.COLOR_BGR2GRAY)
        ret, img_thresh = cv2.threshold(img_gray2,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        msg = self.bridge.cv2_to_imgmsg(img_thresh,"bgr8")
        self.img_pub.publish(msg)
        
    
if __name__ == "__main__" :
    rospy.init_node("libbot")
    bot = libbot()
    rospy.spin()

