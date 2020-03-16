import time
import threading
import sys
from TcpServer import clientTest


load = True
printError = True

while load:

    try:
        from Cmd.CmdControler import CmdControler
        from TcpServer import TcpServ
        from PlcServer import server

        load = False
        print("\n\n------------start---------------")

    except:
        if printError:
            print("\n\n------------Wait for system reboot---------------", sys.exc_info()[0], sys.exc_info()[1])
            printError = False
            time.sleep(1)

TcpServe = TcpServ.TcpServer()
Cmd = CmdControler()

threading.Thread(target=TcpServe.run, ).start()

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
    threading.Thread(target=server.run).start()
    Cmd.run_cmd()
