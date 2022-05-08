import csv
import cv2
import glob
import pprint
import os

def main():
    csv_name = "driving_log.csv"
    path = "IMG"
    with open(csv_name) as f:
        reader = csv.reader(f)
        drive_data = [row for row in reader]

    for row in drive_data:
        # 中央カメラ画像のファイルパス, 左側カメラ画像のファイルパス, 右側カメラ画像のファイルパス,
        # 角度, スロットル, ブレーキ, スピード
        imagepath = row[0]
        filename = os.path.basename(imagepath)
        filepath = os.path.dirname(imagepath)
        angle = float(row[3])
        throttle = float(row[4])
        brake = float(row[5])
        speed = float(row[6])

        image = cv2.imread("IMG" + os.sep + filename)
        image_copy = image.copy()

        # 学習時のクロッピング範囲を表示する
        imgH, imgW = image.shape[:2]
        cropping = (50, 20, 10, 10) # (top_crop, bottom_crop, left_crop, right_crop)
        y, x = cropping[0], cropping[2]
        h = imgH - cropping[0] - cropping[1]
        w = imgW - cropping[2] - cropping[3]
        cv2.rectangle(image_copy, (x,y), (x+w, y+h), (0,0,255), 2)

        # 左右対称画像を保存する
        image_mirror = cv2.flip(image, 1)
        image_mirror_filename = "m_" + filename
        cv2.imwrite(path + os.sep + image_mirror_filename, image_mirror)

        # 左右対称データを保存する
        row_data = ["", filepath + r"/" + filename, "", -angle, throttle, brake, speed]
        with open(csv_name, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row_data)

        cv2.imshow("", image_copy)
        key = cv2.waitKey(0) & 0xFF
        if key == 27:   # esc
            break
    cv2.destroyAllWindows()



if __name__=="__main__":
    main()