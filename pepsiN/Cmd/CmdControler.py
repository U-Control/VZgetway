from TcpServer.TcpServSensor import TcpServSensor
from TcpServer.TcpServPLC import TcpServPLC
from .CmdView import CmdView
from .CmdM import Cmd
import time
from TcpServer.sensorDataProcessing import TypeData
from _ast import If


class CmdControler:

    sensors_server = TcpServSensor()
    plc_server =None
    cmdM: Cmd = Cmd()
    cmd_view: CmdView = None

    # def recived_data_to_cmd_view(self):
    #     self.cmdM.parse_data_from_sensor

    def __init__(self):
        self.cmd_view = CmdView(self.handel_data,self.update_sensors_server)
        self.plc_server =TcpServPLC()
        self.sensors_server.function_process_data_to_view = self.cmdM.parse_data_from_sensor
        self.sensors_server.update_conected_sensors=self.cmd_view.update_conected_sensors 
        self.sensors_server.update_cmd_view=self.update_cmd_view 
        self.plc_server.update_conected_plc=self.cmd_view.update_conected_plc

    def run_cmd(self):
        self.cmd_view.run()


    def update_sensors_server(self,sensor_id,key,value=None):
        self.sensors_server.update_sensors_server(sensor_id,key,value)
        
    def update_cmd_view(self,key,value):
        self.cmd_view.update_cmd_view(key,value)
        
    def handel_data(self, data,isPLC=False,error_message=None):
       
        if error_message:
            self.cmd_view.show_error(error_message)
            return False
        if(isPLC):
            self.plc_server.send_to_plc(data)
            return True
        
        error_message = self.cmdM.pars_cmd(data)

        self.cmd_view.show_error(error_message)
        if error_message:
            return False
        # if self.cmdM.data:
        self.cmd_view.show_error(self.send_data())
        return True
    def get_no_of_times_to_be_send(self, data: str):
         
        type_data=TypeData(data[0]).name
        if type_data in ["debuge_buffer","vz_param"]: 
            return 1
        
        return 3
        
        
        
    def send_data(self):
        sensors_to_send = list(self.sensors_server.dict_allSensor_by_id.keys()) if self.cmdM.id == 'all' \
            else [int(self.cmdM.id)]
        print( self.cmdM.data)
        i = 0
        no_of_times_to_be_send=self.get_no_of_times_to_be_send(self.cmdM.data)
        while i < no_of_times_to_be_send:
            i += 1
            r = self.sensors_server.send_to_sensor(sensors_to_send, self.cmdM.data)
            time.sleep(1)
            
       
      
        return r


