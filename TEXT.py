import wx
import wx.grid
from time import localtime,strftime
import sqlite3

ID_NEW_ENTRY = 160
ID_FINISH_ENTRY = 161
ID_START_SIGNIN = 190
ID_END_SIGNIN = 191
ID_OPEN_RECORD = 283
ID_CLOSE_RECORD = 284
ID_STUDENT_SIGN = -1

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
        self.sigin_time = "08:20;00"

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
            self.knew_time_info = []
            self.knew_stu_id = []
            self.knew_stu_name = []
            self.knew_if_late = []
            cu.execute('select stu_id,stu_name,time_info,if_late from Sign_Info')
            res = cu.fetchall()
            for row in res:
                print(row[0])
                self.knew_stu_id.append(row[0])
                print(row[1])
                self.knew_stu_name.append(row[1])
                print(row[2])
                self.knew_time_info.append(row[2])
                print(row[3])
                self.knew_if_late.append(row[3])
        cu.close()
        conn.commit()
        conn.close()

app = wx.App()
frame = SCIS()
frame.Show()
app.MainLoop()


