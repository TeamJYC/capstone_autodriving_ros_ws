#!/usr/bin/env python

import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import cv2

class Processor:
    def __init__(self):
        self._bridge=CvBridge()
        self._pub = rospy.Publisher("image_processed",Image,queue_size = 10)
        self._sub = rospy.Subscriber("/image_raw",Image,self.callback)

       # self._face = cv2.CascadeClassifier(cv2.samples.findFile('haarcascades/haarcascade_frontalface_default.xml'))
    def callback(self,data):
        cv_image=self._bridge.imgmsg_to_cv2(data,"bgr8")
        low_res = cv2.blur(cv_image,(50,50))
        msg = self._bridge.cv2_to_imgmsg(low_res,"bgr8")
        self._pub.publish(msg)

if __name__=="__main__":
    rospy.init_node("bridge")
    p = Processor()
    rospy.spin()
