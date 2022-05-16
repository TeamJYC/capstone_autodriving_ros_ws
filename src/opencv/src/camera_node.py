#! /usr/bin/env python
# coding:utf-8

import cv2
import numpy as np
import rospy
from std_msgs.msg import Header
from sensor_msgs.msg import Image
from cv_bridge import CvBridge , CvBridgeError
import time

if __name__=="__main__":
    capture = cv2.VideoCapture(0)
    rospy.init_node('camera_node',anonymous=True)
    image_pub=rospy.Publisher('/image_raw', Image, queue_size = 1)
    rate = rospy.Rate(0.3)
    while not rospy.is_shutdown():
        start = time.time()
        ret, frame = capture.read()
        if ret:
            frame = cv2.flip(frame,1)
            ros_frame=Image()
            header=Header(stamp=rospy.Time.now())
            header.frame_id="Camera"
            ros_frame.header=header
            ros_frame.width=640
            ros_frame.height=480
            ros_frame.encoding="bgr8"
            ros_frame.step=1920
            ros_frame.data=np.array(frame).tostring()
            image_pub.publish(ros_frame)
            end = time.time()
            print("cost time:", end-start)
            sleep(3.)
            #rate = rospy.Rate(0.3)
    rate.sleep()
    capture.release()
    cv2.destroyAllWindows()
    print("quit successfully!")

