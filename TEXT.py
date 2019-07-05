import wx
import wx.grid
import sqlite3
from time import localtime,strftime
import os
from skimage import io as iio
import io
import zlib
import dlib
import numpy as np
import cv2
import _thread

ID_NEW_ENTRY = 160
ID_FINISH_ENTRY = 161

ID_START_SIGNIN = 190
ID_END_SIGNIN = 191

ID_OPEN_RECORD = 283
ID_CLOSE_RECORD = 284

ID_STUDENT_SIGN = -1

PATH_FACE = "data/face_img_database/"
facerec = dlib.face_recognition_model_v1("E:/model/dlib_face_recognition_resnet_model_v1.dat")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('E:/model/shape_predictor_68_face_landmarks.dat')

def return_Eucdiatance(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dist = np.sqrt(np.sum(np.square(vec1 - vec2)))
    print("欧式距离: ", dist)
    if dist > 0.4:
        return "difference"
    else:
        return "same"

class SCIS(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,parent=None,title="学生签到系统",size=(920,560))

        self.initMenu()
        self.initInfopanel()
        self.initMainpanel()
        self.initDatabase()
        self.initData()

    def initData(self):
        self.name = ""
        self.id =ID_STUDENT_SIGN
        self.face_info = ""
        self.pic_num = 0
        self.face_entry = False
        self.signin_time = "08:00:00"
        self.callDataBase(1)

    def initMenu(self):

        menuBar = wx.MenuBar()
        menu_Font = wx.Font()
        menu_Font.SetPointSize(14)
        menu_Font.SetWeight(wx.BOLD)

        entryMenu = wx.Menu()
        self.new_entry = wx.MenuItem(entryMenu,ID_NEW_ENTRY,"新建录入")
        self.new_entry.SetBitmap(wx.Bitmap("drawable/new_entry.png"))
        self.new_entry.SetTextColour("SLATE BLUE")
        self.new_entry.SetFont(menu_Font)
        entryMenu.Append(self.new_entry)

        self.finish_entry = wx.MenuItem(entryMenu,ID_FINISH_ENTRY,"完成录入")
        self.finish_entry.SetBitmap(wx.Bitmap("drawable/finish_entry.png"))
        self.finish_entry.SetTextColour("SLATE BLUE")
        self.finish_entry.SetFont(menu_Font)
        self.finish_entry.Enable(False)
        entryMenu.Append(self.finish_entry)


        signinMenu = wx.Menu()
        self.start_signin = wx.MenuItem(signinMenu,ID_START_SIGNIN,"开始签到")
        self.start_signin.SetBitmap(wx.Bitmap("drawable/start_signin.png"))
        self.start_signin.SetTextColour("SLATE BLUE")
        self.start_signin.SetFont(menu_Font)
        signinMenu.Append(self.start_signin)

        self.end_signin = wx.MenuItem(signinMenu,ID_END_SIGNIN,"结束签到")
        self.end_signin.SetBitmap(wx.Bitmap("drawable/end_signin.png"))
        self.end_signin.SetTextColour("SLATE BLUE")
        self.end_signin.SetFont(menu_Font)
        self.end_signin.Enable(False)
        signinMenu.Append(self.end_signin)

        recordMenu = wx.Menu()
        self.open_record = wx.MenuItem(recordMenu,ID_OPEN_RECORD,"打开日志")
        self.open_record.SetBitmap(wx.Bitmap("drawable/open_record.png"))
        self.open_record.SetFont(menu_Font)
        self.open_record.SetTextColour("SLATE BLUE")
        recordMenu.Append(self.open_record)

        self.close_record = wx.MenuItem(recordMenu, ID_CLOSE_RECORD, "关闭日志")
        self.close_record.SetBitmap(wx.Bitmap("drawable/close_record.png"))
        self.close_record.SetFont(menu_Font)
        self.close_record.SetTextColour("SLATE BLUE")
        recordMenu.Append(self.close_record)

        menuBar.Append(entryMenu,"&人脸录入")
        menuBar.Append(signinMenu,"&刷脸签到")
        menuBar.Append(recordMenu,"&考勤日志")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,self.OnNewEntryClicked,id=ID_NEW_ENTRY)
        self.Bind(wx.EVT_MENU,self.OnFinishEntryClicked,id=ID_FINISH_ENTRY)
        self.Bind(wx.EVT_MENU,self.OnStartSigninClicked,id=ID_START_SIGNIN)
        self.Bind(wx.EVT_MENU,self.OnEndSigninClicked,id=ID_END_SIGNIN)
        self.Bind(wx.EVT_MENU,self.OnOpenRecordClicked,id=ID_OPEN_RECORD)
        self.Bind(wx.EVT_MENU,self.OnCloseRecordClicked,id=ID_CLOSE_RECORD)

    def OnOpenRecordClicked(self,event):
        self.callDataBase(2)
        grid = wx.grid.Grid(self,pos=(320,0),size=(600,500))
        grid.CreateGrid(100, 4)
        for i in range(100):
            for j in range(4):
                grid.SetCellAlignment(i,j,wx.ALIGN_CENTER,wx.ALIGN_CENTER)
        grid.SetColLabelValue(0, "学号")
        grid.SetColLabelValue(1, "姓名")
        grid.SetColLabelValue(2, "签到时间")
        grid.SetColLabelValue(3, "是否迟到")

        grid.SetColSize(0,100)
        grid.SetColSize(1,100)
        grid.SetColSize(2,150)
        grid.SetColSize(3,150)

        grid.SetCellTextColour("NAVY")
        for i,id in enumerate(self.Sign_Info_id):
            grid.SetCellValue(i,0,str(id))
            grid.SetCellValue(i,1,self.Sign_Info_name[i])
            grid.SetCellValue(i,2,self.Sign_Info_time_info[i])
            grid.SetCellValue(i,3,self.Sign_Info_if_late[i])

        pass

    def OnCloseRecordClicked(self,event):
        self.initMainpanel()
        pass

    def entry_cap(self,event):
        self.cap = cv2.VideoCapture(0)
        while self.cap.isOpened():
            flag, img_read = self.cap.read()
            kk = cv2.waitKey(1)
            dets = detector(img_read, 1)

            if len(dets) != 0:
                biggest_face = dets[0]
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top()-det.bottom()
                    if w*h > maxArea:
                        biggest_face = det
                        maxArea = w*h

                cv2.rectangle(img_read, tuple([biggest_face.left(), biggest_face.top()]),
                                      tuple([biggest_face.right(), biggest_face.bottom()]),
                                      (255, 0, 0), 2)
                img_height, img_width = img_read.shape[:2]
                image1 = cv2.cvtColor(img_read, cv2.COLOR_BGR2RGB)
                pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
                self.bmp.SetBitmap(pic)

                shape = predictor(img_read, biggest_face)
                features_cap = facerec.compute_face_descriptor(img_read, shape)

                for i,knew_face_info in enumerate(self.knew_face_info):
                    compare = return_Eucdiatance(features_cap, knew_face_info)
                    if compare == "same":
                        self.infoText.AppendText(self.getDateTime()+"学号:"+str(self.knew_id[i])
                                                 +" 姓名:"+self.knew_name[i]+" 的人脸数据已存在\r\n")
                        self.face_entry = True
                        self.OnFinishEntry()
                        _thread.exit()

                face_height = biggest_face.bottom()-biggest_face.top()
                face_width = biggest_face.right()- biggest_face.left()
                im_blank = np.zeros((face_height, face_width, 3), np.uint8)
                try:
                    for ii in range(face_height):
                        for jj in range(face_width):
                            im_blank[ii][jj] = img_read[biggest_face.top() + ii][biggest_face.left() + jj]

                    if len(self.name)>0:
                        cv2.imencode('.jpg', im_blank)[1].tofile(
                        PATH_FACE + self.name + "/img_face_" + str(self.pic_num) + ".jpg")
                        self.pic_num += 1
                        print("写入本地：", str(PATH_FACE + self.name) + "/img_face_" + str(self.pic_num) + ".jpg")
                        self.infoText.AppendText(self.getDateTime()+"图片:"+str(PATH_FACE + self.name) + "/img_face_" + str(self.pic_num) + ".jpg保存成功\r\n")
                except:
                    print("保存照片异常,请对准摄像头")

                if  self.new_entry.IsEnabled():
                    _thread.exit()
                if self.pic_num == 10:
                    self.OnFinishEntry()
                    _thread.exit()

    def OnNewEntryClicked(self,event):
        self.new_entry.Enable(False)
        self.finish_entry.Enable(True)
        self.callDataBase(1)
        while self.id == ID_STUDENT_SIGN:
            self.id = wx.GetNumberFromUser(message="请输入您的学号",
                                           prompt="学号", caption="提示",
                                           value=ID_STUDENT_SIGN,
                                           parent=self.bmp,max=100000000,min=ID_STUDENT_SIGN)
            for knew_id in self.knew_id:
                if knew_id == self.id:
                    self.id = ID_STUDENT_SIGN
                    wx.MessageBox(message="学号已存在，请重新输入", caption="提示")

        while self.name == '':
            self.name = wx.GetTextFromUser(message="请输入您的的姓名,用于创建姓名文件夹",
                                           caption="提示",
                                      default_value="", parent=self.bmp)

            for exsit_name in (os.listdir(PATH_FACE)):
                if self.name == exsit_name:
                    wx.MessageBox(message="姓名文件夹已存在，请重新输入", caption="警告")
                    self.name = ''
                    break
        os.makedirs(PATH_FACE+self.name)
        _thread.start_new_thread(self.entry_cap,(event,))
        pass

    def OnFinishEntry(self):
        self.new_entry.Enable(True)
        self.finish_entry.Enable(False)
        self.cap.release()
        self.bmp.SetBitmap(wx.Bitmap(self.index_pic))
        if self.face_entry == True:
            dir = PATH_FACE + self.name
            for file in os.listdir(dir):
                os.remove(dir+"/"+file)
                print("已删除已录入人脸的图片", dir+"/"+file)
            os.rmdir(PATH_FACE + self.name)
            print("已删除已录入人脸的姓名文件夹", dir)
            self.initData()
            return
        if self.pic_num>0:
            pics = os.listdir(PATH_FACE + self.name)
            feature_list = []
            feature_average = []
            for i in range(len(pics)):
                pic_path = PATH_FACE + self.name + "/" + pics[i]
                print("正在读的人脸图像：", pic_path)
                img = iio.imread(pic_path)
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                dets = detector(img_gray, 1)
                if len(dets) != 0:
                    shape = predictor(img_gray, dets[0])
                    face_descriptor = facerec.compute_face_descriptor(img_gray, shape)
                    feature_list.append(face_descriptor)
                else:
                    face_descriptor = 0
                    print("未在照片中识别到人脸")
            if len(feature_list) > 0:
                for j in range(128):
                    feature_average.append(0)
                    for i in range(len(feature_list)):
                        feature_average[j] += feature_list[i][j]
                    feature_average[j] = (feature_average[j]) / len(feature_list)
                self.insertARow([self.id,self.name,feature_average],1)
                self.infoText.AppendText(self.getDateTime()+"学号:"+str(self.id)
                                     +" 姓名:"+self.name+" 的人脸数据已成功存入\r\n")
            pass

        else:
            os.rmdir(PATH_FACE + self.name)
            print("已删除空文件夹",PATH_FACE + self.name)
        self.initData()

    def OnFinishEntryClicked(self,event):
        self.OnFinishEntry()
        pass

    def sign_cap(self,event):
        self.cap = cv2.VideoCapture(0)
        while self.cap.isOpened():
            flag, img_read = self.cap.read()
            kk = cv2.waitKey(1)
            dets = detector(img_read, 1)

            if len(dets) != 0:
                biggest_face = dets[0]
                maxArea = 0
                for det in dets:
                    w = det.right() - det.left()
                    h = det.top() - det.bottom()
                    if w * h > maxArea:
                        biggest_face = det
                        maxArea = w * h

                cv2.rectangle(img_read, tuple([biggest_face.left(), biggest_face.top()]),
                              tuple([biggest_face.right(), biggest_face.bottom()]),
                              (255, 0, 255), 2)
                img_height, img_width = img_read.shape[:2]
                image1 = cv2.cvtColor(img_read, cv2.COLOR_BGR2RGB)
                pic = wx.Bitmap.FromBuffer(img_width, img_height, image1)
                self.bmp.SetBitmap(pic)

                shape = predictor(img_read, biggest_face)
                features_cap = facerec.compute_face_descriptor(img_read, shape)

                for i, knew_face_info in enumerate(self.knew_face_info):
                    compare = return_Eucdiatance(features_cap, knew_face_info)
                    if compare == "same":
                        print("same")
                        flag = 0
                        nowdt = self.getDateTime()
                        for j,Sign_Info_name in enumerate(self.Sign_Info_name):
                            if Sign_Info_name == self.knew_name[i]  and  nowdt[0:nowdt.index(" ")] == self.Sign_Info_time_info[j][0:self.Sign_Info_time_info[j].index(" ")]:
                                self.infoText.AppendText(nowdt+"学号:"+ str(self.knew_id[i])
                                                 + " 姓名:" + self.knew_name[i] + " 签到失败,重复签到\r\n")
                                flag = 1
                                break

                        if flag == 1:
                            break

                        if nowdt[nowdt.index(" ")+1:-1] <= self.signin_time:
                            self.infoText.AppendText(nowdt + "学号:" + str(self.knew_id[i])
                                                 + " 姓名:" + self.knew_name[i] + " 成功签到,且未迟到\r\n")
                            self.insertARow([self.knew_id[i],self.knew_name[i],nowdt,"否"],1)
                        else:
                            self.infoText.AppendText(nowdt + "学号:" + str(self.knew_id[i])
                                                     + " 姓名:" + self.knew_name[i] + " 成功签到,但迟到了\r\n")
                            self.insertARow([self.knew_id[i], self.knew_name[i], nowdt, "是"], 2)
                        self.callDataBase(2)
                        break

                if self.start_signin.IsEnabled():
                    self.bmp.SetBitmap(wx.Bitmap(self.index_pic))
                    _thread.exit()

    def OnStartSigninClicked(self,event):
        self.start_signin.Enable(False)
        self.end_signin.Enable(True)
        self.callDataBase(2)
        _thread.start_new_thread(self.sign_cap,(event,))
        pass

    def OnEndSigninClicked(self,event):
        self.start_signin.Enable(True)
        self.end_signin.Enable(False)
        pass

    def initInfopanel(self):
        resultText = wx.StaticText(parent=self, pos = (10,20),size=(90, 60))
        resultText.SetBackgroundColour('red')
        self.info = "\r\n"+self.getDateTime()+"程序初始化成功\r\n"
        self.infoText = wx.TextCtrl(parent=self,size=(320,500),
                   style=(wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY))

        self.infoText.SetForegroundColour("ORANGE")
        self.infoText.SetLabel(self.info)
        font = wx.Font()
        font.SetPointSize(12)
        font.SetWeight(wx.BOLD)
        font.SetUnderlined(True)

        self.infoText.SetFont(font)
        self.infoText.SetBackgroundColour('TURQUOISE')
        pass

    def initMainpanel(self):
        self.index_pic = wx.Image("E:/drawable/index.png", wx.BITMAP_TYPE_ANY).Scale(600, 500)
        self.bmp = wx.StaticBitmap(parent=self, pos=(320,0), bitmap=wx.Bitmap(self.index_pic))
        pass

    def getDateTime(self):
        dateandtime = strftime("%Y-%m-%d %H:%M:%S",localtime())
        return "["+dateandtime+"]"

    def initDatabase(self):
        conn = sqlite3.connect("inspurer.db")
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

    def adapt_array(self,arr):
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        dataa = out.read()
        return sqlite3.Binary(zlib.compress(dataa, zlib.Z_BEST_COMPRESSION))

    def convert_array(self,text):
        out = io.BytesIO(text)
        out.seek(0)
        dataa = out.read()
        out = io.BytesIO(zlib.decompress(dataa))
        return np.load(out)

    def insertARow(self,Row,type):
        conn = sqlite3.connect("inspurer.db")
        cu = conn.cursor()
        if type == 1:
            cu.execute("insert into Stu_Info (id,name,face_info) values(?,?,?)",
                    (Row[0],Row[1],self.adapt_array(Row[2])))
            print("写人脸数据成功")
        if type == 2:
            cu.execute("insert into Sign_Info (id,name,time_info,if_late) values(?,?,?,?)",
                        (Row[0],Row[1],Row[2],Row[3]))
            print("写日志成功")
            pass

        cu.close()
        conn.commit()
        conn.close()
        pass

    def callDataBase(self,type):
        conn = sqlite3.connect("inspurer.db")
        cu = conn.cursor()

        if type == 1:
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
        if type == 2:
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
        pass

app = wx.App()
frame = SCIS()
frame.Show()
app.MainLoop()