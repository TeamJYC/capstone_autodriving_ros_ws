#! /usr/bin/env python
# coding:utf-8

import cv2
import numpy as np
import rospy
from std_msgs.msg import Header
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import time

DELAY_N_SECONDS = 3

#capture = cv2.VideoCapture(0)

#def get_frame_every_nseconds():
#    ret, frame = capture.read()
#    time.sleep(DELAY_N_SECONDS)
#    return frame

#def camera_release():
#    capture.release()



if __name__=="__main__":
    capture = cv2.VideoCapture(0) # 
    rospy.init_node('camera_node', anonymous=True) #
    image_pub=rospy.Publisher('/image_view/image_raw', Image, queue_size = 1) #
    
    rate = rospy.Rate(0.3)
    while not rospy.is_shutdown():    # Ctrl C, 비정상 종료 시 에러 보고. device busy！
        start = time.time()
        ret, frame = capture.read()
        #rospy.sleep(3.)
        if ret: # 화면이 있으면 다시 실행
            # frame = cv2.flip(frame,0)   # 수직 미러 작동
            frame = cv2.flip(frame,1)   #   수평 미러 작동
    
            ros_frame = Image()
            header = Header(stamp = rospy.Time.now())
            header.frame_id = "Camera"
            ros_frame.header=header
            ros_frame.width = 640
            ros_frame.height = 480
            ros_frame.encoding = "bgr8"
            ros_frame.step = 1920
            ros_frame.data = np.array(frame).tostring() #이미지 형식 변환
            image_pub.publish(ros_frame) #
            end = time.time()  
            print("cost time:", end-start ) # 각 프레임의 실행 시간을 확인하여 적절한rate
            #rate = rospy.Rate(0.3) # 0.3hz
        rate.sleep()        
        


    capture.release()
    cv2.destroyAllWindows() 
    print("quit successfully!")