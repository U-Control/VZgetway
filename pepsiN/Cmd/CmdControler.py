from TcpServer.TcpServ import TcpServer
from .CmdView import CmdView
from .CmdM import Cmd


class CmdControler:

    server = TcpServer()
    cmdM: Cmd = Cmd()
    cmd_view: CmdView = None

    # def recived_data_to_cmd_view(self):
    #     self.cmdM.parse_data_from_sensor

    def __init__(self):
        self.cmd_view = CmdView(self.handel_data)
        self.server.function_process_data_to_view = self.cmdM.parse_data_from_sensor



    def run_cmd(self):
        self.cmd_view.run()

    def handel_data(self, data):
        error_message = self.cmdM.pars_cmd(data)

        self.cmd_view.show_error(error_message)
        if error_message:
            return False
        # if self.cmdM.data:
        self.cmd_view.show_error(self.send_data())
        return True

    def send_data(self):
        sensors_to_send = list(self.server.dict_allSensor_by_id.keys()) if self.cmdM.id == 'all' \
            else [int(self.cmdM.id)]
        print( self.cmdM.data)
        r = self.server.send_to_sensor(sensors_to_send, self.cmdM.data,self.cmdM.read_raw_data_in_seconds)
        self.cmdM.read_raw_data_in_seconds = None
        return r


