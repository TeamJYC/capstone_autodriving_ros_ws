#!/usr/bin/env python
#coding:utf-8

from __future__ import print_function
import sys
import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge,CvBridgeError
import cv2
import numpy as np
import requests
import xml.etree.ElementTree as ET
from collections import Counter
import ocr
reload(sys)
sys.setdefaultencoding('utf8')

global callnum_queue, isnbn_queue
callnum_queue, isbn_queue = [], []

def get_callnum(text):
    count = 0
    text = text.replace(" ", "")
    for idx, val in enumerate(text):
        if (ord(val) >= 48 and ord(val) <= 57):
            count +=1
        else:
            count = 0

        if count == 3:
            callnum_single = text[idx-2:idx+1]
            callnum_queue.append(callnum_single)
            getcallnum = True

           # print(callnum_single)

            if len(callnum_queue) == 10:
                callnum_queue.pop(0)

            callnum_counter = Counter(callnum_queue)

            if int(callnum_counter.most_common(1)[0][1]) >= 3:
                callnum = callnum_counter.most_common(1)[0][0]
                return callnum

            break

def get_isbn(text):
    count = 0
    text = text.replace(" ", "")

    for idx, val in enumerate(text):

        if (ord(val) >= 48 and ord(val) <= 57):
            count += 1
            
        else:
            count = 0

        if count == 13:
            isbn_single = text[idx-12:idx+1]
            isbn_queue.append(isbn_single)

            #print(isbn_single)

            if len(isbn_queue) == 10:
                isbn_queue.pop(0)

            isbn_counter = Counter(isbn_queue)

            if int(isbn_counter.most_common(1)[0][1] >= 2:
                    isbn = isbn_counter.most_common(1)[0][0]
                    return isbn

            break


def callnum_to_kdx(callnum):
    kdc = callnum[0]
    return kdc

def isbn_to_kdc(isbn):
    host = 'https://www.nl.go.kr/NL'
    path = '/search/openApi/search.do?'
    key = 'a3678243a7ca64ca37c6ff5edb7cf7f3ef12f378fbad97de528d0f32769798a1'
    params = {'key' : key, 'detailSearch' : 'true', 'isbnOp' : 'isbn', 'isbnCode' : isbn}
    url = host+path
    result = requests.get(url,params=params)
    xmlstr = result.text
    root = ET.fromstring(xmlstr)
    kdc = root.find('result').find('item').find('kdc_code_1s').text

def watershed(img_gray, img_source):
    
    img_shape = np.zeros_like(img_gray)
    
    ret, img_thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU) # 이진화

    kernel = np.ones((3,3),np.uint8)
    
    img_opening = cv2.morphologyEx(img_thresh,cv2.MORPH_OPEN,kernel,iterations=2) # 잡음 제거

    sure_bg = cv2.dilate(img_opening,kernel,iterations=3) # 배경 요소 확보(bg)

    dist_transform = cv2.distanceTransform(img_opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.5*dist_transform.max(),255,0)
    sure_fg = np.uint8(sure_fg) # skeleton 이미지 & 다시 이진화(fg)

    unknown = cv2.subtract(sure_bg, sure_fg) # bg, fg 제외 영역

    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    
    markers = cv2.watershed(img_source, markers)
    img_shape[markers == -1] = 255
    h,w = img_shape.shape
    img_shape[0,:] = 0
    img_shape[:,0] = 0
    img_shape[h-1,:] = 0
    img_shape[:,w-1] = 0
    
    return img_shape


def perspective_transformation(img, img_source):
    
    contours, ret = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 컨투어링(테두리)

    cnt = contours[0]
    
    epsilon = 0.1*cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True) # 외곽선 근사화
    
    if len(approx) != 4: # 꼭짓점이 4개가 나오지 않을 때 임의로 좌표값 설정
        pts1 = np.float32([[0,0], [0,0], [0,0], [0,0]])
    else : # 꼭짓점이 정상적으로 4개 나오면 꼭짓점 설정 맞추고 투시 변환
        mean = approx.mean(axis = 2).squeeze()
        idx_sort = mean.argsort()
        sub = approx[idx_sort[1]] - approx[idx_sort[2]]
        
        if sub[0][0] > 0:
                a = idx_sort[1]
                b = idx_sort[2]
        else:
                a = idx_sort[2]
                b = idx_sort[1]    
        pts1 = np.float32([approx[idx_sort[0]], approx[a], approx[b], approx[idx_sort[3]]])   
    
    pts2 = np.float32([[0,0], [500,0], [0,500], [500,500]])
    
    M = cv2.getPerspectiveTransform(pts1, pts2)
    
    img_warp = cv2.warpPerspective(img_source, M, (500,500))
    
    return img_warp


#def clache(img):
#    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
#
#    img_clahe = img_yuv.copy()
#    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)) #CLAHE 생성
#    img_clahe[:,:,0] = clahe.apply(img_clahe[:,:,0])           #CLAHE 적용
#    img_clahe = cv2.cvtColor(img_clahe, cv2.COLOR_YUV2BGR)
    
#    return img_clahe

def Procbot():
    def __init__(self):
        self.bridge = CvBridge()
        #self.img_pub = rospy.Publisher("text_ocr",String,queue_size=10)
        self.img_pub = rospy.Publisher("image_thres",Image,queue_size=10)
        self.img_sub = rospy.Subscriber("/image_raw",Image,self.callback)

    def callback(self,data):
        img = self.bridge.imgmsg_to_cv2(data,"bgr8")
        #cv2.imread('test.jpg', cv2.IMREAD_COLOR)
        
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        img_watershed = watershed(img_gray, img)
        
        img_warp = perspective_transformation(img_watershed, img)
        
        #img_clache = clache(img_warp)
        
        #img_gray2 = cv2.cvtColor(img_clache, cv2.COLOR_BGR2GRAY)
        img_gray2 = cv2.cvtColor(img_warp,cv2.COLOR_BGR2GRAY)
        kernel = np.array([[1, 1, 1, 1, 1, 1, 1]])
        gray_kernel = np.dot(kernel.T, kernel)
        img_graymop = cv2.dilate(img_gray2, gray_kernel, iterations = 1)
        img_sub2 = 255 - cv2.absdiff(img_gray2, img_graymop)
        ret, img_thresh2 = cv2.threshold(img_sub2, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        text_ocr = ocr.tesseract(img_thresh2)
        hello = "%s"%text_ocr
        rospy.loginfo(hello)

        msg = self.bridge.cv2_to_imgmsg(img_thresh2,"mono8")
        self.img_pub.publish(msg)
        
        #key = cv2.waitKey(33)
        #if key == 27: # Esc
        #    break
   # cv2.destroyAllWindows()

if __name__=="__main__":
    rospy.init_node("img_process_node")
    bot = Procbot()
    rospy.spin()
