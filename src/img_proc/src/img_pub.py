#!/usr/bin/python
#coding:utf-8
import roslib
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge,CvBridgeError

    
def talker():
    cap = cv2.VideoCapture(0)
    rospy.init_node("img_pub",anonymous=True)
    img_pub = rospy.Publisher("/image_raw",Image)
    bridge = CvBridge()

    while not rospy.is_shutdown():
        ret, cv_image = cap.read()
        img_pub.publish(bridge.cv2_to_imgmsg(cv_image,"bgr8"))
        cv2.waitKey(1);
    
    rospy.spin()
    cap.release()
    cv2.destroyAllWindows()
    

if __name__ =="__main__":
    talker()

