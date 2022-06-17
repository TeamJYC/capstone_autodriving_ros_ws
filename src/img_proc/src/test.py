#!/usr/bin/env python

import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import String
import numpy as np
import cv2
import watershed
import perspective
import clache
import getcallnum
import ocr
import sys
import time
reload(sys)
sys.setdefaultencoding('utf8')

class Processor:
    def __init__(self):
        self._bridge=CvBridge()
        self._pub = rospy.Publisher("image_processed",Image,queue_size = 10)
        #self._pub = rospy.Publisher("ocr_processed",String,queue_size = 10)

        self._sub = rospy.Subscriber("/image_raw",Image,self.callback)

       # self._face = cv2.CascadeClassifier(cv2.samples.findFile('haarcascades/haarcascade_frontalface_default.xml'))
    def callback(self,data):
        cv_img=self._bridge.imgmsg_to_cv2(data,"bgr8")
       # low_res = cv2.blur(cv_image,(50,50))
        cv_gray=cv2.cvtColor(cv_img,cv2.COLOR_BGR2GRAY)
        img_shape = watershed.watershed(cv_gray,cv_img)
        img_warp = perspective.perspective_transformation(img_shape,cv_img)

        img_gray2 = cv2.cvtColor(img_warp, cv2.COLOR_BGR2GRAY)
        kernel = np.array([[1, 1, 1, 1, 1, 1, 1]])
        gray_kernel = np.dot(kernel.T, kernel)
        img_graymop = cv2.dilate(img_gray2, gray_kernel, iterations = 1)
        img_sub2 = 255 - cv2.absdiff(img_gray2, img_graymop)
        ret,img_thresh2 = cv2.threshold(img_sub2, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        text_ocr = ocr.tesseract(img_thresh2)
        hello = "hello ocr %s" %text_ocr
        time.sleep(1)
        rospy.loginfo(hello)
        
        msg = self._bridge.cv2_to_imgmsg(img_thresh2,"mono8")
        self._pub.publish(msg)

if __name__=="__main__":
    rospy.init_node("bridge")
    p = Processor()
    rospy.spin()
