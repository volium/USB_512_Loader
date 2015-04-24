import wx
import sys
from pywinusb import hid
from intelhex import IntelHex


# Device information table
device_info_map = dict()
device_info_map['at90usb1287'] = {'page_size': 256, 'flash_kb': 128}
device_info_map['at90usb1286'] = {'page_size': 256, 'flash_kb': 128}
device_info_map['at90usb647']  = {'page_size': 256, 'flash_kb': 64}
device_info_map['at90usb646']  = {'page_size': 256, 'flash_kb': 64}
device_info_map['atmega32u4']  = {'page_size': 128, 'flash_kb': 32}
device_info_map['atmega32u2']  = {'page_size': 128, 'flash_kb': 32}
device_info_map['atmega16u4']  = {'page_size': 128, 'flash_kb': 16}
device_info_map['atmega16u2']  = {'page_size': 128, 'flash_kb': 16}
device_info_map['at90usb162']  = {'page_size': 128, 'flash_kb': 16}
device_info_map['atmega8u2']   = {'page_size': 128, 'flash_kb': 8}
device_info_map['at90usb82']   = {'page_size': 128, 'flash_kb': 8}

valid_hid_devices = []

def get_hid_devices():
    hid_device_filter = hid.HidDeviceFilter(vendor_id=0x03EB, product_id=0x2067)

    valid_hid_devices = hid_device_filter.get_devices()

    return valid_hid_devices

    # if len(valid_hid_devices) is 0:
        # return None
    # else:
        # return valid_hid_devices[0]

def send_page_data(hid_device, address, data):
    # Bootloader page data should be the HID Report ID (always zero) followed
    # by the starting address to program, then one device's flash page worth
    # of data
    output_report_data = [0]
    output_report_data.extend([address & 0xFF, address >> 8])
    output_report_data.extend(data)

    hid_device.send_output_report(output_report_data)

def program_device(hex_data, device_info, current_device_selected):
    valid_hid_devices = get_hid_devices()
    hid_device = valid_hid_devices[current_device_selected]

    if hid_device is None:
        print("No valid HID device found.")
        sys.exit(1)

    try:
        hid_device.open()
        print("Connected to bootloader.")

        # Program in all data from the loaded HEX file, in a number of device
        # page sized chunks
        for addr in range(0, hex_data.maxaddr(), device_info['page_size']):
            # Compute the address range of the current page in the device
            current_page_range = range(addr, addr+device_info['page_size'])

            # Extract the data from the hex file at the specified start page
            # address and convert it to a regular list of bytes
            page_data = [hex_data[i] for i in current_page_range]

            print("Writing address 0x%04X-0x%04X" % (current_page_range[0], current_page_range[-1]))

            # Devices with more than 64KB of flash should shift down the page
            # address so that it is 16-bit (page size is guaranteed to be
            # >= 256 bytes so no non-zero address bits are discarded)
            if device_info['flash_kb'] < 64:
                send_page_data(hid_device, addr, page_data)
            else:
                send_page_data(hid_device, addr >> 8, page_data)

        # Once programming is complete, start the application via a dummy page
        # program to the page address 0xFFFF
        print("Programming complete, starting application.")
        send_page_data(hid_device, 0xFFFF, [0] * device_info['page_size'])

    finally:
        hid_device.close()


class FileDrop(wx.FileDropTarget):
   """File Drop Class"""

   def __init__(self, window):
      wx.FileDropTarget.__init__(self)
      self.window = window

   def OnDropFiles(self, x, y, filenames):

      for name in filenames:
         try:
            self.window.filebrowser.SetPath(name)
            self.window.filebrowser.GetTextCtrl().SetInsertionPointEnd()
         except IOError, error:
            dlg = wx.MessageDialog(None, 'Error opening file\n' + str(error))
            dlg.ShowModal()
         except UnicodeDecodeError, error:
            dlg = wx.MessageDialog(None, 'Cannot open non ascii files\n' + str(error))
            dlg.ShowModal()


class MainPanel(wx.Panel):
   """Main Application Panel"""

   def __init__(self, *args, **kwargs):
      """Create Main Application Panel"""

      wx.Panel.__init__(self, *args, **kwargs)

      # Sizers
      vsizer = wx.BoxSizer(wx.VERTICAL)
      hsizer1 = wx.BoxSizer(wx.HORIZONTAL)
      hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
      hsizer3 = wx.BoxSizer(wx.HORIZONTAL)

      # Controls (window elements)
      self.label1 = wx.StaticText(self, label='Load Hex File:', style=wx.ALIGN_LEFT)
      self.filebrowser = wx.FilePickerCtrl(self, style = wx.FLP_OPEN|wx.FLP_FILE_MUST_EXIST|wx.FLP_USE_TEXTCTRL)
      self.progressbar = wx.Gauge(self, range = 100, size = (100, 25), style = wx.GA_HORIZONTAL|wx.GA_SMOOTH)

      self.devicescombobox = wx.ComboBox(self, value = "Device to program", choices = [], style = wx.CB_DROPDOWN|wx.CB_READONLY)

      sampleList = get_hid_devices()
      # Here we dynamically add our values to the second combobox.
      for item in sampleList:
         self.devicescombobox.Append(str(item.vendor_id))


      fileDropTarget = FileDrop(self)
      self.SetDropTarget(fileDropTarget)

      # Layout hsizer1
      hsizer1.Add(self.label1, flag=wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
      hsizer1.Add(self.filebrowser, proportion=1, flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)

      # Layout hsizer2
      hsizer2.Add(self.devicescombobox, proportion=1, flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)

      # Layout hsizer3
      hsizer3.Add(self.progressbar, proportion=1, flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)

      # Events
      self.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnPickFileEvent, self.filebrowser)
      self.Bind(wx.EVT_COMBOBOX, self.OnDeviceChosenEvent, self.devicescombobox)

      # Layout vsizer
      vsizer.Add(hsizer1, flag=wx.EXPAND|wx.ALL, border=10)
      vsizer.Add(hsizer2, flag=wx.EXPAND|wx.ALL, border=5)
      vsizer.Add(hsizer3, flag=wx.EXPAND|wx.ALL, border=5)

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




   def OnPickFileEvent(self, evt):

      # Load the specified HEX file
      try:
         self.hex_data = IntelHex(self.filebrowser.GetPath())
      except:
         print("Could not open the specified HEX file.")

      # self.filebrowser.GetTextCtrl().SetInsertionPointEnd()
      # self.timer.Start(100)
      # pass

   def OnDeviceChosenEvent(self, evt):
      current_device_selected =  self.devicescombobox.GetCurrentSelection()
      program_device(self.hex_data, device_info, current_device_selected)
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

   current_device_selected = 0

   device_info = device_info_map['atmega32u4']
   app = wx.App()
   HidLoaderGUI(None, title='HID Bootloader')
   app.MainLoop()