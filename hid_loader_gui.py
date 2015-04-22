import wx
import sys
import pywinusb
import intelhex

class MainPanel(wx.Panel):
   """Main Application Panel"""

   def __init__(self, *args, **kwargs):
      """Create Main Application Panel"""

      wx.Panel.__init__(self, *args, **kwargs)

      # Sizers
      vsizer = wx.BoxSizer(wx.VERTICAL)
      hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
      hsizer2 = wx.BoxSizer(wx.HORIZONTAL)

      # Controls (window elements)
      self.label1 = wx.StaticText(self, label='Load Hex File:', style=wx.ALIGN_LEFT)
      self.filebrowser = wx.FilePickerCtrl(self, style = wx.FLP_OPEN|wx.FLP_FILE_MUST_EXIST|wx.FLP_USE_TEXTCTRL)
      self.progressbar = wx.Gauge(self, range = 100, size = (100, 25), style = wx.GA_HORIZONTAL|wx.GA_SMOOTH)

      # Layout hsizer1
      hsizer1.Add(self.label1, flag=wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
      hsizer1.Add(self.filebrowser, proportion=1, flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)

      # Layout hsizer2
      hsizer2.Add(self.progressbar, proportion=1, flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)

      # Events
      self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnPickFile, self.filebrowser)

      # Layout vsizer
      vsizer.Add(hsizer1, flag=wx.EXPAND|wx.ALL, border=10)
      vsizer.Add(hsizer2, flag=wx.EXPAND|wx.ALL, border=5)

      self.Bind(wx.EVT_TIMER, self.TimerHandler)
      self.timer = wx.Timer(self)
      self.count = 0
      self.maxrange = self.progressbar.GetRange()

      # Panel sizer
      self.SetSizer(vsizer)


   def TimerHandler(self, event):
        self.count += 1

        self.progressbar.SetValue(self.count)

        if self.count == self.maxrange:
            self.timer.Stop()




   def OnPickFile(self, evt):
      self.filebrowser.GetTextCtrl().SetInsertionPointEnd()
      self.timer.Start(100)
      pass


class HidLoaderGUI(wx.Frame):
   """Main Application Frame."""

   def __init__(self, *args, **kwargs):
      """Create Main Application Frame."""

      wx.Frame.__init__(self, *args, **kwargs)

      self.Panel = MainPanel(self)
      self.Centre()
      self.Show()







if __name__ == '__main__':
   app = wx.App()
   HidLoaderGUI(None, title='HID Bootloader')
   app.MainLoop()