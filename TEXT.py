import wx
import wx.grid
from time import localtime,strftime
import sqlite3
import numpy as np
import dlib
import os
import _thread
from skimage import io as iio
import io

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


class SCIS(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent = None,title = "学生签到系统",size = (920,560))
        self.initMenu()
        self.initDataBase()
        self.initData()

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
        for i,stu_id in enumerate(self.Sign_Info_stu_id):
            grid.SetCellValue(i,0,str(stu_id))
            grid.SetCellValue(i,1,self.Sign_Info_stu_names(i))
            grid.SetCellValue(i,2,self.Sign_Info_time_info(i))
            grid.SetCellValue(i,3,self.Sign_Info_if_late(i))
    def entry_cap(self,event):
        pass

    def OnNewEntryClicked(self,event):
        self.new_entry.Enable(False)
        self.finish_entry.Enable(True)
        self.callDataBase(1)
        while self.knew_stu_id== ID_STUDENT_SIGN:
            self.knew_stu_id= wx.GetNumberFromUser(message="请输入您的学号",prompt="学号",caption= "提示",value= ID_STUDENT_SIGN,
                                               min = ID_STUDENT_SIGN,max = 100000000000)
            for knew_stu_id in self.knew_stu_id:
                if knew_stu_id == self.stu_id:
                    self.knew_stu_id = ID_STUDENT_SIGN
                    wx.MessageBox(message = "学号已存在，请再次输入",caption = "提示")
        while self.name == '':
            self.name = wx.GetTextFromUser(message="请输入您的的姓名,用于创建姓名文件夹",
                                           caption="温馨提示",
                                           default_value="")

            # 监测是否重名
            for exsit_name in (os.listdir(PATH_FACE)):
                if self.name == exsit_name:
                    wx.MessageBox(message="姓名文件夹已存在，请重新输入", caption="警告")
                    self.name = ''
                    break
        os.makedirs(PATH_FACE + self.name)
        _thread.start_new_thread(self.entry_cap, (event,))
        pass


    def getDateTime(self):
        datetime = strftime("%Y-%m-%d %H:%M:%S", localtime())
        return "[" + datetime + "]"

    def initDataBase(self):
        conn = sqlite3.connect("sqlite.db")
        cu = conn.cursor()
        cu.execute('''create table if not exists Stu_Info(
            stu_name text not null,
            stu_id int not null primary key,
            face_info array not null)''')
        cu.execute('''create table if not exists Sign_Info(
            time_info text not null,
            stu_id int not null,
            stu_name text not null,
            if_late text not null)''')
        cu.close()
        conn.commit()
        conn.close()

    def callDataBase(self,flag):
        conn = sqlite3.connect("sqlite.db")
        cu = conn.cursor()
        if flag == 1:
            self.knew_stu_id = []
            self.knew_stu_name = []
            self.knew_face_info = []
            cu.execute('select stu_id,stu_name,face_info from Stu_Info')
            res = cu.fetchall()
            for row in res:
                print(row[0])
                self.knew_stu_id.append(row[0])
                print(row[1])
                self.knew_stu_name.append(row[1])
                print(row[2])
                self.knew_face_info.append(row[2])
        if flag == 2:
            self.Sign_Info_stu_id = []
            self.Sign_Info_stu_name = []
            self.Sign_Info_time_info = []
            self.Sign_Info_if_late = []
            cu.execute('select stu_id,stu_name,time_info,if_late from Sign_Info')
            res = cu.fetchall()
            for row in res:
                print(row[0])
                self.Sign_Info_stu_id.append(row[0])
                print(row[1])
                self.Sign_Info_stu_name.append(row[1])
                print(row[2])
                self.Sign_Info_time_info.append(row[2])
                print(row[3])
                self.Sign_Info_if_late.append(row[3])

app = wx.App()
frame = SCIS()
frame.Show()
app.MainLoop()


