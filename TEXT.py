import wx

ID_NEW_ENTRY = 160
ID_FINISH_ENTRY = 161
ID_START_SIGNIN = 190
ID_END_SIGNIN = 191


class SCIS(wx.Frame):

    def __init__(self, parent, title):
        super(SCIS, self).__init__(parent, title=title, size=(120, 560))
        self.InitUI()

    def InitUI(self):
        menubar = wx.MenuBar()
        menu_Font = wx.Font()#Font(facename = "consolas",pointsize = 20)
        menu_Font.SetPointSize(14)
        menu_Font.SetWeight(wx.BOLD)

        entryMenu = wx.Menu()
        self.new_entry = wx.MenuItem(entryMenu,ID_NEW_ENTRY,"新的录入")
        self.new_entry.SetBitmap(wx.Bitmap("drawable/new_entry.png"))
        self.new_entry.SetTextColour("BLUE")
        self.new_entry.SetFont(menu_Font)
        entryMenu.Append(self.new_entry)

        self.finish_entry = wx.MenuItem(entryMenu, ID_FINISH_ENTRY, "完成录入")
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




        fileMenu1 = wx.Menu()
        fileMenu2 = wx.Menu()
        fileMenu3 = wx.Menu()
        menubar.Append(fileMenu1, '&人脸录入')
        menubar.Append(fileMenu2, '&刷脸签到')
        menubar.Append(fileMenu3, '&出勤记录')
        self.SetMenuBar(menubar)
        self.text = wx.TextCtrl(self, -1, style=wx.EXPAND | wx.TE_MULTILINE)
        self.Bind(wx.EVT_MENU, self.menuhandler)
        self.SetSize((1000, 800))
        self.Centre()
        self.Show(True)

    def menuhandler(self, event):
        id = event.GetId()
        if id == wx.ID_NEW:
            self.text.AppendText("new" + "\n")

app = wx.App()
SCIS(None, '学生签到系统')
app.MainLoop()


