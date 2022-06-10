#!/usr/bin/python
#coding:utf-8

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge,CvBridgeError
import cv2

bridge = CvBridge()

def callback(msg):
    img = 
    

def listener():
    rospy.init_node('img_sub')
    rospy.Subscriber("/image_raw",Image,callback)
    rospy.spin()
    
if __name__ == "__main__" :
        listener()


