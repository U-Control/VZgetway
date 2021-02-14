import time
import threading
import sys
import logging
from properties.PropertiesReader import ConfParams  
#import win32api, win32process, win32con
from win32 import win32api, win32process
import win32.lib.win32con as win32con
#import win32process, win32con
#from win32 import win32api, win32process, win32con
 
from http.server import  HTTPServer
from RestAPI import server

#run the Rest server
# def run(server_class=HTTPServer, handler_class=S, port=8001):
#     logging.basicConfig(level=logging.INFO)
#     server_address = ('', port)
#     httpd = server_class(server_address, handler_class)
#     logging.info('Starting httpd...port:'+str(port)+'\n')
#     try:
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#         pass
#     httpd.server_close()
#     logging.info('Stopping httpd...\n')
#     
def setpriority(pid=None,priority=1):
    """ Set The Priority of a Windows Process.  Priority is a value between 0-5 where
        2 is normal priority.  Default sets the priority of the current
        python process but can take any valid process ID. """
        
   
    
#     priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
#                        win32process.BELOW_NORMAL_PRIORITY_CLASS,
#                        win32process.NORMAL_PRIORITY_CLASS,
#                        win32process.ABOVE_NORMAL_PRIORITY_CLASS,
#                        win32process.HIGH_PRIORITY_CLASS,
#                        win32process.REALTIME_PRIORITY_CLASS]
#     if pid == None:
pid = win32api.GetCurrentProcessId()
handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)
params=ConfParams()
#system( params.getParam("GATEWAY_NAME"))

load = True
printError = True

while load:

    try:
        from Cmd.CmdControler import CmdControler 
        from TcpServer import TcpServSensor
        from TcpServer import TcpServPLC
    
        load = False
        print("\n\n------------start---------------")

    except:
        if printError:
            print("\n\n------------Wait for system reboot---------------", sys.exc_info()[0], sys.exc_info()[1])
           
            # sys.exc_info().
            printError = False
            time.sleep(1)

TcpServeSensor = TcpServSensor.TcpServSensor()
TcpServePLC = TcpServPLC.TcpServPLC()
Cmd = CmdControler()

threading.Thread(target=TcpServeSensor.run, ).start()
#threading.Thread(target=run, ).start()
# Demo
# clientTest.init_socket(1)
# threading.Thread(target=clientTest.send_data,args=(1,)).start()
# threading.Thread(target=clientTest.handle_client_connection).start()

# threading.Thread(target=TcpServe.send_data_test,args=(1,)).start()
# threading.Thread(target=TcpServe.send_data_test,args=(3,)).start()
# threading.Thread(target=TcpServe.send_data_test,args=(4,)).start()
# threading.Thread(target=TcpServe.send_data_test,args=(5,)).start()
# threading.Thread(target=TcpServe.send_data_test,args=(6,)).start()
# threading.Thread(target=TcpServe.send_data_test,args=(7,)).start()
# threading.Thread(target=TcpServe.send_data_test,args=(8,)).start()
#
# d.start()
#
#

if __name__ == '__main__':
    # threading.Thread(target=server.run).start()
    threading.Thread(target=server.run_server).start()
    Cmd.run_cmd()
