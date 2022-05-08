import imp
import cv2
import glob
import os
from PIL import Image
import numpy as np

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (0,255,0)
GREEN = (0,0,255)
YELLOW = (255,255,0)

def morph_image(image):
    # 輪郭を抽出する
    import pprint
    pts = []
    colors=[RED, GREEN, BLUE, YELLOW]
    for i in range(4):
        mask = np.full(image.shape, colors[i], np.uint8)
        cv2.imshow("mask", mask)
        cond = np.where(image==mask, WHITE, BLACK)
        # pprint.pprint(cond)
        rows = np.any(cond, axis=1)
        cols = np.any(cond, axis=0)
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        print(colors[i], y_min, y_max ,x_min, x_max )
        pass


    h1, w1 = image.shape[:2]
    h2, w2 = 400, 600
    pts1 = np.float32([(0,0), (0,h1), (w1,h1), (w1,0)])
    pts2 = np.float32([(0,0), (0,h2), (w2,h2), (w2,0)])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    return cv2.warpPerspective(image, M, (w2,h2), borderValue=(255,255,255))


folder = "labels"
files = glob.glob(folder + os.sep + "*")

for file in files:
    imgPIL = Image.open(file)
    imgCV = np.array(imgPIL, np.uint8)
    cv2.imshow("1", imgCV)
    cv2.imshow("2", morph_image(imgCV))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    1/0
