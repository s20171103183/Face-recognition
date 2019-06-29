import wx
import wx.grid
from time import localtime,strftime
import sqlite3
import numpy as np
import dlib
import os
import _thread
import cv2

ID_NEW_ENTRY = 160
ID_FINISH_ENTRY = 161
ID_START_SIGNIN = 190
ID_END_SIGNIN = 191
ID_OPEN_RECORD = 283
ID_CLOSE_RECORD = 284
ID_STUDENT_SIGN = -1

PATH_FACE = "data/face_img_database"
facerec = dlib.face_recognition_model_v1("E:/model/dlib_face_recognition_resnet_model_v1.dat")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("E:/model/shape_predictor_68_face_landmarks.dat")
def return_Eucdiatance(vec1,vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    distance = np.sqrt(np.sum(np.square(vec1-vec2)))
    print("欧氏距离：",distance)
    if distance > 0.4:
        return "difference"
    else:
        return "same"

class SCIS(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent = None,title = "学生签到系统",size = (920,560))
        self.initMenu()
        self.initDataBase()
        self.initData()
        self.initMainpanel()
        self.initInfopanel()

    def initData(self):
        self.name = ""
        self.id = ID_STUDENT_SIGN
        self.face_info = ""
        self.pic_num = 0
        self.flag_entry = False
        self.sigin_time = "08:00;00"
        self.callDataBase(1)

    def initMenu(self):
        menubar = wx.MenuBar()
        menu_Font = wx.Font()
        menu_Font.SetPointSize(14)
        menu_Font.SetWeight(wx.BOLD)

        entryMenu = wx.Menu()
        self.new_entry = wx.MenuItem(entryMenu,ID_NEW_ENTRY,"新的录入")
        self.new_entry.SetBitmap(wx.Bitmap("drawable/new_entry.png"))
        self.new_entry.SetTextColour("BLUE")
        self.new_entry.SetFont(menu_Font)
        entryMenu.Append(self.new_entry)

        self.finish_entry = wx.MenuItem(entryMenu, ID_FINISH_ENTRY,  "完成录入")
        self.finish_entry.SetBitmap(wx.Bitmap("drawable/finish_entry.png"))
        self.finish_entry.SetTextColour("BLUE")
        self.finish_entry.SetFont(menu_Font)
        self.finish_entry.Enable(False)
        entryMenu.Append(self.finish_entry)

        signinMenu = wx.Menu()
        self.start_signin = wx.MenuItem(signinMenu,ID_START_SIGNIN,"开始签到")
        self.start_signin.SetBitmap(wx.Bitmap("drawable/start_signin.png"))
        self.start_signin.SetTextColour("BLUE")
        self.start_signin.SetFont(menu_Font)
        signinMenu.Append(self.start_signin)

        self.end_signin = wx.MenuItem(signinMenu, ID_END_SIGNIN, "完成签到")
        self.end_signin.SetBitmap(wx.Bitmap("drawable/endt_signin.png"))
        self.end_signin.SetTextColour("BLUE")
        self.end_signin.SetFont(menu_Font)
        self.end_signin.Enable(False)
        signinMenu.Append(self.end_signin)

        recordMenu = wx.Menu()
        self.open_record = wx.MenuItem(recordMenu,ID_OPEN_RECORD,"打开记录")
        self.open_record.SetBitmap(wx.Bitmap("drawable/open_record.png"))
        self.open_record.SetTextColour("BLUE")
        self.open_record.SetFont(menu_Font)
        recordMenu.Append(self.open_record)

        self.close_record = wx.MenuItem(recordMenu, ID_CLOSE_RECORD, "关闭记录")
        self.close_record.SetBitmap(wx.Bitmap("drawable/close_record.png"))
        self.close_record.SetTextColour("BLUE")
        self.close_record.SetFont(menu_Font)
        recordMenu.Append(self.close_record)

        menubar.Append(entryMenu,'&人脸录入')
        menubar.Append(signinMenu,'&刷脸签到')
        menubar.Append(recordMenu,'&出勤记录')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnOpenRecordClicked, id=ID_OPEN_RECORD)
        self.Bind(wx.EVT_MENU, self.OnNewEntryClicked, id=ID_NEW_ENTRY)
        self.Bind(wx.EVT_MENU, self.OnCloseRecordClicked, id=ID_CLOSE_RECORD)
        self.Bind(wx.EVT_MENU, self.OnFinishEntryClicked, id=ID_FINISH_ENTRY)
    def OnOpenRecordClicked(self,event):
        self.callDataBase(2)
        grid = wx.grid.Grid(self,pos = (320,0),size = (600,500))
        grid.CreateGrid(100,4)
        for i in range(100):
            for j in range(4):
                grid.SetCellAlignment(i,j,wx.ALIGN_CENTER,wx.ALIGN_CENTRE)
        grid.SetColLabelValue(0,"学号")
        grid.SetColLabelValue(1,"姓名")
        grid.SetColLabelValue(2,"签到时间")
        grid.SetColLabelValue(3,"是否迟到")

        grid.SetColSize(0,100)
        grid.SetColSize(1,100)
        grid.SetColSize(2,150)
        grid.SetColSize(3,150)
        grid.SetCellTextColour("BLACK")
        for i,stu_id in enumerate(self.Sign_Info_id):
            grid.SetCellValue(i,0,str(id))
            grid.SetCellValue(i,1,self.Sign_Info_name(i))
            grid.SetCellValue(i,2,self.Sign_Info_time_info(i))
            grid.SetCellValue(i,3,self.Sign_Info_if_late(i))
    def OnCloseRecordClicked(self,event):
        self.initMainpanel()

    def entry_cap(self,event):
        self.cap = cv2.VideoCapture(0)
        while self.cap.isOpened():
            flag,img_read = self.cap.read()
            kk = cv2.waitKey(0.1)
            dets = detector(img_read,1)

            if len(dets) != 0:
                biggest_face = dets[0]
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top() - det.bottom()
                    if w*h > maxArea:
                        biggest_face = det
                        maxArea = w*h
                cv2.rectangle(img_read,tuple([biggest_face.left(),biggest_face.top()]),
                                       tuple([biggest_face.right(),biggest_face.bottom()]),
                              (0,255,0),2)
                img_read.height,img_read.width = img_read.shape[:2]
                image1 = cv2.cvtColor(img_read,cv2.COLOR_BGR2RGB)
                pic = wx.Bitmap.FromBuffer(img_read.height,img_read.width,image1)
                self.bmp.SetBitmap(pic)
                shape = predictor(img_read,biggest_face)
                features_cap = facerec.compute_face_descriptor(img_read,shape)

                for i,knew_face_info in enumerate(self.knew_face_info):
                    compare = return_Eucdiatance(features_cap,knew_face_info)
                    if compare == "same":
                        self.infoText.AppendText(self.getDateTime() + "学号" + str(self.knew_id[i]) +
                                                "姓名" + self.knew_name[i] + "人脸数据已存在\r\n")
                        self.flag_entry = True
                        self.OnFinishEntryClicked()
                        _thread.exit()

                face_height = biggest_face.bottom() - biggest_face.top()
                face_width = biggest_face.right() - biggest_face.left()
                img_blank = np.zeros((face_height,face_width,3),np.unit8)
                try:
                    for ii in range(face_height):
                        for jj in range(face_width):
                            img_blank[ii][jj] = img_read[biggest_face.top() + ii][biggest_face.left() + jj]
                    if len(self.name) > 0:
                        cv2.imencode('jpg',img_blank)[1].tofile(
                            PATH_FACE + self.name + "/_img_face_" + str(self.pic_num) + ".jpg")
                        self.pic_num += 1
                        self.infoText.AppendText(self.getDateTime() + "图片：" + str(PATH_FACE + self.name) +
                                        "/img_face" + str(self.pic_num) + ".jpg保存成功\r\n")
                except:
                    print("保存照片异常，请对准摄像头")
                if self.new_entry.IsEnabled():
                    _thread.exit()
                if self.pic_num == 10:
                    self.OnFinishEntryClicked()
                    _thread.exit()

    def OnFinishEntry(self):
        self.new_entry.IsEnabled(True)
        self.finish_entry.IsEnabled(False)
        self.cap.release()
        self.bmp.SetBitmap(wx.Bitmap(self.index_pic))
        if self.flag_entry == True:
            dir = PATH_FACE + self.name
    def sign_cap(self):
        self.cap = cv2.VideoCapture(0)
        while self.cap.isOpened():
            flag, im_rd = self.cap.read()
            kk = cv2.waitKey(1)
            dets = detector(im_rd, 1)

            if len(dets) != 0:
                biggest_face = dets[0]
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top() - det.bottom()
                    if w * h > maxArea:
                        biggest_face = det
                        maxArea = w * h

                cv2.rectangle(im_rd, tuple([biggest_face.left(), biggest_face.top()]),
                              tuple([biggest_face.right(), biggest_face.bottom()]),
                              (255, 0, 255), 2)
                img_height, img_width = im_rd.shape[:2]
                image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
                pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
                self.bmp.SetBitmap(pic)

                shape = predictor(im_rd, biggest_face)
                features_cap = facerec.compute_face_descriptor(im_rd, shape)

                for i, knew_face_info in enumerate(self.knew_face_info):
                    # 将某张人脸与存储的所有人脸数据进行比对
                    compare = return_Eucdiatance(features_cap, knew_face_info)
                    if compare == "same":  # 找到了相似脸
                        print("same")
                        flag = 0
                        nowdt = self.getDateAndTime()
                        for j, logcat_name in enumerate(self.logcat_name):
                            if logcat_name == self.knew_name[i] and nowdt[0:nowdt.index(" ")] == self.logcat_datetime[
                                                                                                     j][
                                                                                                 0:self.logcat_datetime[
                                                                                                     j].index(" ")]:
                                self.infoText.AppendText(nowdt + "工号:" + str(self.knew_id[i])
                                                         + " 姓名:" + self.knew_name[i] + " 签到失败,重复签到\r\n")
                                flag = 1
                                break

                        if flag == 1:
                            break

                        if nowdt[nowdt.index(" ") + 1:-1] <= self.puncard_time:
                            self.infoText.AppendText(nowdt + "工号:" + str(self.knew_id[i])
                                                     + " 姓名:" + self.knew_name[i] + " 成功签到,且未迟到\r\n")
                            self.insertARow([self.knew_id[i], self.knew_name[i], nowdt, "否"], 1)
                        else:
                            self.infoText.AppendText(nowdt + "工号:" + str(self.knew_id[i])
                                                     + " 姓名:" + self.knew_name[i] + " 成功签到,但迟到了\r\n")
                            self.insertARow([self.knew_id[i], self.knew_name[i], nowdt, "是"], 2)
                        self.callDataBase(2)
                        break

    def OnFinishEntryClicked(self, event):
        pass
    def OnNewEntryClicked(self,event):
        self.new_entry.Enable(False)
        self.finish_entry.Enable(True)
        self.callDataBase(1)
        while self.id== ID_STUDENT_SIGN:
            self.id= wx.GetNumberFromUser(message="请输入您的学号",prompt="学号",caption= "提示",value= 0,
                                               min = ID_STUDENT_SIGN,max = 9999999)
            for knew_id in self.knew_id:
                if knew_id == self.id:
                    self.id = ID_STUDENT_SIGN
                    wx.MessageBox(message = "学号已存在，请再次输入",caption = "提示")
        while self.name == '':
            self.name = wx.GetTextFromUser(message="请输入您的的姓名,用于创建姓名文件夹",
                                           caption="提示",
                                           default_value="")
            for exsit_name in (os.listdir(PATH_FACE)):
                if self.name == exsit_name:
                    wx.MessageBox(message="姓名文件夹已存在，请重新输入", caption="警告")
                    self.name = ''
                    break
        os.makedirs(PATH_FACE + self.name)
        _thread.start_new_thread(self.entry_cap, (event,))

    def initInfopanel(self):
        resultText = wx.StaticText(parent = self,pos = (10,20),size = (90,60))
        resultText.SetBackgroundColour("red")
        self.info = "\r\n" + self.getDateTime() + "程序初始化成功\r\n"
        self.infoText = wx.TextCtrl(parent = self,size = (320,500),
                                    style = wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY)
        self.infoText.SetForegroundColour("GREEN")
        self.infoText.SetLabel(self.info)
        font = wx.Font()
        font.SetPointSize(12)
        font.SetWeight(wx.BOLD)
        font.SetUnderlined(True)

        self.infoText.SetFont(font)
        self.infoText.SetBackgroundColour("GRAY")

    def initMainpanel(self):
        self.index_pic = wx.Image("E:/drawable/index.png",wx.BITMAP_TYPE_ANY).Scale(600,500)
        self.bmp = wx.StaticBitmap(parent = self, pos = (320,0), bitmap = wx.Bitmap(self.index_pic))

    def getDateTime(self):
        datetime = strftime("%Y-%m-%d %H:%M:%S", localtime())
        return "[" + datetime + "]"

    def initDataBase(self):
        conn = sqlite3.connect("insuper.db")
        cu = conn.cursor()
        cu.execute('''create table if not exists Stu_Info
                (name text not null,
                id int not null primary key,
                face_info array not null)''')
        cu.execute('''create table if not exists Sign_Info
                 (time_info text not null,
                 id int not null,
                 name text not null,
                 if_late text not null)''')

        cu.close()
        conn.commit()
        conn.close()

    def callDataBase(self,flag):
        conn = sqlite3.connect("insuper.db")
        cu = conn.cursor()
        if flag == 1:
            self.knew_id = []
            self.knew_name = []
            self.knew_face_info = []
            cu.execute('select id,name,face_info from Stu_Info')
            res = cu.fetchall()
            for row in res:
                print(row[0])
                self.knew_id.append(row[0])
                print(row[1])
                self.knew_name.append(row[1])
                print(self.convert_array(row[2]))
                self.knew_face_info.append(self.convert_array(row[2]))

        if flag == 2:
            self.Sign_Info_id = []
            self.Sign_Info_name = []
            self.Sign_Info_time_info = []
            self.Sign_Info_if_late = []
            cu.execute('select id,name,time_info,if_late from Sign_Info')
            res = cu.fetchall()
            for row in res:
                print(row[0])
                self.Sign_Info_id.append(row[0])
                print(row[1])
                self.Sign_Info_name.append(row[1])
                print(row[2])
                self.Sign_Info_time_info.append(row[2])
                print(row[3])
                self.Sign_Info_if_late.append(row[3])


app = wx.App()
frame = SCIS()
frame.Show()
app.MainLoop()


