import csv
from sqlite3 import Cursor
import cv2
import glob
import os
import math

from requests import delete

def main():
    path = r"morishima_data/"
    os.chdir(path)

    csv_name = "driving_log.csv"
    with open(csv_name) as f:
        reader = csv.reader(f)
        drive_data = [row for row in reader]

    i = 0
    while 0 <= i < len(drive_data):
        row = drive_data[i]
        # 中央カメラ画像のファイルパス, 左側カメラ画像のファイルパス, 右側カメラ画像のファイルパス,
        # 角度, スロットル, ブレーキ, スピード
        imagepath = row[0]
        filename = os.path.basename(imagepath)
        filepath = os.path.dirname(imagepath)
        delete_flag = row[2]
        angle = float(row[3])
        throttle = float(row[4])
        brake = float(row[5])
        speed = float(row[6])

        image = cv2.imread("IMG" + os.sep + filename)
        h,w = image.shape[:2]

        if delete_flag == "":
            cv2.rectangle(image, (0,0), (w-1, h-1), (0,0,0), 5)

        cx, cy, r = 160, 80, 60
        cv2.circle(image, (cx, cy), r, (0,0,255), 1)
        x0 = cx + int(r*math.sin(angle))
        y0 = cy - int(r*math.cos(angle))
        cv2.line(image, (x0, y0), (cx, cy), (0,0,255), 2)
        cv2.putText(image, f"frame={i}", (10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
        cv2.imshow("", image)
        key = cv2.waitKeyEx(0)
        if key==27:     #esc
            break
        if key==ord("r"):       # 1フレーム戻る
            i += -2
        if key==ord("d"):
            drive_data[i][2] = "" if drive_data[i][2]!="" else True
        else:
            i += 1

    cv2.destroyAllWindows()



if __name__=="__main__":
    main()