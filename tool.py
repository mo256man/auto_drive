import tkinter as tk
from turtle import bgcolor
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import os
import time
import random
import math
import glob
import sys

# グローバル変数（クラス変数にするのが面倒なので）
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (0,255,0)
GREEN = (0,0,255)
YELLOW = (255,255,0)


class Application(tk.Frame):
    def __init__(self, master=None, image_folder=None, label_folder=None):
        super().__init__(master)
        self.create_widgets()

        self.max_pts = 4                                # 四角形を作る
        self.image_folder = image_folder
        self.label_folder = label_folder

        # ファイル一覧（パスは含まないので都度指定する）
        self.files = [os.path.basename(f) for f in glob.glob(self.image_folder + os.sep + "*")]
        self.file_cnt = len(self.files)
        self.cnt = 0
        self.file = self.files[self.cnt]                # 最初のファイル名

        self.init_image()


    def create_widgets(self):
        '''ウィジェットを作成する'''

        self.canvas_width, self.canvas_height = 640, 480

        self.master.title("ラベル作成くん")    # ウィンドウタイトル
        self.master.geometry("1280x720") # ウィンドウサイズ(幅x高さ)
        
        label_title = tk.Label(self.master, text="ラベル作成くん", font=("MSゴシック",40))
        self.filename = tk.StringVar()
        self.filename.set("ファイル名")
        self.label_filename = tk.Label(self.master, textvariable=self.filename, font=("MSゴシック",20))
        self.canvas1 = tk.Canvas(self.master, width=self.canvas_width, height=self.canvas_height, bg="cyan")
        self.canvas2 = tk.Canvas(self.master, width=self.canvas_width, height=self.canvas_height)

        label_title.pack()
        self.label_filename.pack()
        self.canvas1.place(x=0, y=200)
        self.canvas2.place(x=640, y=200)

        self.canvas1.bind("<Motion>", self.mouse_move)
        self.canvas1.bind("<Button-1>", self.mouse_lclick)
        self.canvas1.bind("<B1-Motion>", self.drag)
        self.canvas1.bind("<Button-3>", self.mouse_rclick)
        self.master.bind("<Key>", self.input_key)
        self.master.focus_set()



    def init_image(self):
        """画像初期化"""
        self.filename.set(self.file)                    # ファイル名表示
        self.pts = []                                   # 座標群リセット
        self.image_origin = Image.open(self.image_folder + os.sep + self.file)
        self.image_copy = self.image_origin.copy()

        """画像をキャンバスに合わせたサイズで表示"""
        w, h = self.image_origin.size
        if w/h > self.canvas_width/self.canvas_height:
            self.bai = self.canvas_width / w
            showW = self.canvas_width
            showH = int(h / w * showW)
        else:
            self.bai = self.canvas_height / h
            showH = self.canvas_height
            showW = int(w / h * showH)
        self.image_shown_origin = self.image_copy.resize((showW, showH))
        self.image_shown = self.image_shown_origin.copy()
        self.image_tmp = self.image_shown_origin.copy()
        self.draw()


    def draw(self):
        self.tk_image = ImageTk.PhotoImage(self.image_tmp)
        self.canvas1.create_image(0, 0, anchor=tk.NW, image=self.tk_image)


    def input_key(self, event):
        key = event.keysym

        if key=="Escape":           # escで終了
            print("quit")
            self.master.destroy()
            sys.exit()

        elif key=="Right":          # Rightで次の画像へ
            self.next_image(1)    

        elif key=="Left":           # Leftで前の画像へ
            self.next_image(-1)    
    
    def next_image(self, k=1):
        if k>0:                     # 次へ　最後ならば最初へ
            self.cnt = self.cnt+1 if self.cnt < self.file_cnt-1 else 0
        else:                       # 前へ　最初ならば最後へ
            self.cnt = self.cnt-1 if self.cnt >0 else self.file_cnt-1
        self.file = self.files[self.cnt]
        self.init_image()


    def mouse_move(self, event):
        x, y = event.x, event.y
        self.image_tmp = self.image_shown.copy()
        draw = ImageDraw.Draw(self.image_tmp)

        if len(self.pts) < self.max_pts:        # 最大点数未満の場合

            # ポインタの十字線
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            draw.line([(0,y),(self.canvas_width-1,y)], color, 1)
            draw.line([(x,0),(x,self.canvas_height-1)], color, 1)

            # ひとつ前の点と現在の点を結ぶ線
            if 0 < len(self.pts) < self.max_pts:
                x0 = int(self.pts[-1][0] * self.bai)
                y0 = int(self.pts[-1][1] * self.bai)
                draw.line([(x0,y0), (x,y)], RED, 2)

            # ラス1だったら最初の点との間に線を引く
            if len(self.pts) == self.max_pts - 1:
                x0 = int(self.pts[0][0] * self.bai)
                y0 = int(self.pts[0][1] * self.bai)
                draw.line([(x0,y0), (x,y)], RED, 1)

        else:            # 最大点数の場合
            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
            font = ImageFont.truetype(font="consola.ttf", size=50)
            draw.text((event.x, event.y), "OK?", color, font)

        self.draw()

    def mouse_lclick(self, event):
        """ 左クリック """

        # キャンバス上の座標はドラッグ時に使うので覚えておく
        self.posx = event.x
        self.posy = event.y

        if len(self.pts) < self.max_pts:        # 最大点数未満の場合
            # 描写するのはキャンバス上の画像
            draw = ImageDraw.Draw(self.image_shown)

            # 座標は拡大縮小されたキャンバス上の座標ではなく元画像に対する座標
            x = int(event.x / self.bai)
            y = int(event.y / self.bai)       # 画面上のマウス座標 -> 元画像の座標
            self.pts.append((x, y))                             # 元画像上の座標を記憶する

            # 頂点に点（丸）をプロットする
            x0 = event.x -2
            y0 = event.y -2
            x1 = event.x +2
            y1 = event.y +2
            draw.ellipse((x0,y0,x1,y1), RED)

            # 2点以上記録していたら、ひとつ前の点との間に線を引く
            if len(self.pts) >= 2:
                x0 = int(self.pts[-2][0] * self.bai)
                y0 = int(self.pts[-2][1] * self.bai)
                x1 = event.x
                y1 = event.y
                draw.line([(x0,y0), (x1,y1)], RED, 4)

            # ラス1だったら、最初の点との間に線を引く
            if len(self.pts) == self.max_pts:
                x0 = int(self.pts[0][0] * self.bai)
                y0 = int(self.pts[0][1] * self.bai)
                draw.line([(x0,y0), (x1,y1)], RED, 4)

        else:                       # 最大点数の場合
            self.make_label()       # いま拡大画像で作ったラベルを元画像と同サイズで作る
            self.next_image()       # 次の画像へ    

        self.draw()


    def mouse_rclick(self, event):
        """右クリック時、一手戻る"""
        if len(self.pts) > 0:                               # 座標が1点以上記録されていたら
            self.pts.pop()                                  # 最後の要素を削除する

        self.image_shown = self.image_shown_origin.copy()   # 元画像をリセット
        draw = ImageDraw.Draw(self.image_shown)

        # 削除後に1点以上あったら再度点を描写する
        if len(self.pts) > 0:
            for i in range(len(self.pts)):
                x0 = int(self.pts[i][0] * self.bai) -2
                y0 = int(self.pts[i][1] * self.bai) -2
                x1 = int(self.pts[i][0] * self.bai) +2
                y1 = int(self.pts[i][1] * self.bai) +2
                draw.ellipse((x0,y0,x1,y1), RED)

        # 削除後に2点以上あったら再度線を描写する
        if len(self.pts) >= 2:
            for i in range(len(self.pts)-1):
                x0 = int(self.pts[i][0] * self.bai)
                y0 = int(self.pts[i][1] * self.bai)
                x1 = int(self.pts[i+1][0] * self.bai)
                y1 = int(self.pts[i+1][1] * self.bai)
                draw.line([(x0,y0), (x1,y1)], RED, 4)

        self.image_tmp = self.image_shown.copy()
        self.draw()
    
    def drag(self, event):
        dx = event.x - self.posx
        dy = event.y - self.posy
        self.Var_shiftx.set(self.Var_shiftx.get() + dx)
        self.Var_shifty.set(self.Var_shifty.get() + dy)
        self.click(event)

    def scrl_callback(self, val):
        """ スクロールバーが変化したときに呼ばれるコールバック関数 """
        tmp = self.convert_preview(self.image_shown)
        w = WIDTH
        h = HEIGHT
        image_rgb = cv2.cvtColor(cv2.resize(tmp, (w, h)), cv2.COLOR_BGR2RGB)
        self.image_Tk = ImageTk.PhotoImage(Image.fromarray(image_rgb), master=self.canvas)
        self.canvas.create_image(0, 0, image=self.image_Tk, anchor='nw')
        if self.Chkbox.get():
            self.canvas.create_line(w / 2, 0, w / 2, h, fill='red')
            self.canvas.create_line(0, h / 2, w, h / 2, fill='red')

    def make_label(self):
        mask = Image.new("RGB", self.image_origin.size, BLACK)     # ベースとなる真っ黒画像
        draw = ImageDraw.Draw(mask)
        # draw.polygon(self.pts, WHITE, RED)
        colors=[RED, GREEN, BLUE, YELLOW]
        for pt, color in zip(self.pts, colors):
            x0 = pt[0] - 2
            y0 = pt[1] - 2
            x1 = pt[0] + 2
            y1 = pt[1] + 2
            draw.rectangle((x0, y0, x1, y1), color)

        mask.save(self.label_folder + os.sep + "mask_" + self.file)

if __name__ == "__main__":
    IMAGE_FOLDER = "images"
    LABEL_FOLDER = "labels"

    if not os.path.exists(LABEL_FOLDER):
        os.mkdir(LABEL_FOLDER)

    root = tk.Tk()
    app = Application(master=root, image_folder=IMAGE_FOLDER, label_folder=LABEL_FOLDER)
    app.mainloop()