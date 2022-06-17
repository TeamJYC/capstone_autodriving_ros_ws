# -*- coding: utf-8 -*-
import cv2
import numpy as np
import math
def perspective_transformation(img, img_source):
    
    ret1,contours, ret = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 컨투어링(테두리)
   # img_warp = cv2.drawContours(img_source,contours,-1,(0,255,0),3)

    cnt = contours[0]
 
    epsilon = 0.1*cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, epsilon, True) # 외곽선 근사화
    w = 0
    h = 0
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
        w = int(math.sqrt((approx[idx_sort[0]][0][0]-approx[a][0][0])*(approx[idx_sort[0]][0][0]-approx[a][0][0])+(approx[idx_sort[0]][0][1]-approx[a][0][1])*(approx[idx_sort[0]][0][1]-approx[a][0][1])))
        h = int(math.sqrt((approx[idx_sort[0]][0][0]-approx[b][0][0])*(approx[idx_sort[0]][0][0]-approx[b][0][0])+(approx[idx_sort[0]][0][1]-approx[b][0][1])*(approx[idx_sort[0]][0][1]-approx[b][0][1])))
    pts2 = np.float32([[0,0], [2*w,0], [0,2*h], [2*w,2*h]])
    
    M = cv2.getPerspectiveTransform(pts1, pts2)
    
    img_warp = cv2.warpPerspective(img_source, M, (2*w,2*h))
    return img_warp

