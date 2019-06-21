import wx

app = wx.App()
window = wx.Frame(None, title="学生签到系统", size=(920 , 560))
panel = wx.Panel(window)
label = wx.StaticText(panel, label="学生签到系统", pos=(100, 100))
window.Show(True)
app.MainLoop()

def initMenu(self):
    menuBar = wx.menuBar()
    menuBar.Append("人脸录入")


