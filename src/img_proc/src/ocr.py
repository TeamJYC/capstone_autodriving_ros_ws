#!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import pytesseract
from collections import Counter

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def tesseract(img):
    text = pytesseract.image_to_string(img, lang="kor") # 테서렉트로 글자 추출
    return text

if __name__ == "__main__":
    img = cv2.imread("ocr.jpg")
    text = tesseract(img)
    print(text)
