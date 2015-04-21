import wx
import sys
import pywinusb
import intelhex

class MainPanel(wx.Panel):
   """Main Application Panel"""

   def __init__(self, *args, **kwargs):
      """Create Main Application Panel"""

      wx.Panel.__init__(self, *args, **kwargs)

      vsizer = wx.BoxSizer(wx.VERTICAL)

      hsizer1 = wx.BoxSizer(wx.HORIZONTAL)

      hsizer1.Add(wx.StaticText(self, label='Load Hex File:', style=wx.ALIGN_RIGHT), flag=wx.RIGHT, border=5)

      self.filebrowser = wx.FilePickerCtrl(self, style = wx.FLP_OPEN|wx.FLP_FILE_MUST_EXIST|wx.FLP_USE_TEXTCTRL)
      hsizer1.Add(self.filebrowser, proportion=1, flag=wx.EXPAND)

      self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnPickFile, self.filebrowser)

      vsizer.Add(hsizer1, proportion=0, flag=wx.EXPAND|wx.ALL, border=10)

      self.SetSizer(vsizer)
      
   def OnPickFile(self, evt):
      self.filebrowser.GetTextCtrl().SetInsertionPointEnd()
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