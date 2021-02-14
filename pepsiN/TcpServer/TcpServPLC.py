  
 
from .plcDataProcessing import * 
from ThingBoardConection.client import ThingBoardUser
import logging
from logging.handlers import RotatingFileHandler
from properties.PropertiesReader import ConfParams
from pymodbus3.client.sync import ModbusTcpClient 


class TcpServPLC: 
    instance = None

    class __TcpServer:
        params=ConfParams()
#         get_status = b'\x12\x01\x01'
# 
#         begin_of_packet =b'UUUUU'
        #user = ThingBoardUser()
        
# 
#         function_process_data_to_view = None
        update_conected_plc = None 
        plc_host =  params.getParam("PLC_HOST")
     
        plc_socket=None
        
        # 192.168.1.22:502
        #PLC Mod Bus Regs 40001-40100
#         dict_allSensor_by_id = {}
#         prevPacket=None 
#         prevPacketType=None 
        logger=None
        plc_client=None
        def __init__(self):
            if(self.logger==None):
                self.createLogger ('generalPLCgateway')
            if len(self.plc_host)>1:
                plc_client = ModbusTcpClient(self.plc_host)
            try:
                if len(self.plc_host)>1:
                    result =plc_client.read_holding_registers(0,5,unit=0X01)
                    if len(result.registers)==5:
                        print ("Gateway connected succesfully to PLC : "+str(result))
                #self.update_conected_plc(self.plc_host)
                
                else :
                    print("connection is terminated " )
                    self.logger.error("connection is terminated ")
            except Exception as e:
                    print("error sending data to PLC " + str(e))
                    self.logger.error("error sending data to PLC " + str(e))
            
             
            
            
            
            
        def recv_data(self, client_socket,processData):
#             value=client_socket.recv(100)
#             print("first 100 bytes : ", str(value))
           
            value=client_socket.recv(20)
            if(value== b''):
                self.plc_socket=None
                processData.connection_terminated=True
                return
            
            print("received from PLC :",str(value))
            self.send_to_plc( value)
#             #in case out of reading sync, clearing the socket buffer
#             while(value!=self.begin_of_packet):
#                 print("out of reading sync, clearing the socket buffer")
#                 socketIsNoEmpty=True
#                 while(socketIsNoEmpty):
#                     print("read 10000")
#                     value=client_socket.recv(1024) 
#                     if(len(value)<1024):
#                         socketIsNoEmpty=False
#                 value=client_socket.recv( processData.headersProcess.LENGTH_PACKET_PREFIX)       
#                     
#                     
#             value=client_socket.recv( processData.headersProcess.LENGTH_HEADERS)
#             valueAll=value
#             processData.headersProcess.headers = value
#             #print("hearers : ", str(value))
#             
#             value = client_socket.recv(processData.headersProcess.len_data)
#             processData.headersProcess.data =  value
#             valueAll=valueAll+value;
# #             
# #             if(processData.headersProcess.headers[0]>8 or processData.headersProcess.headers[0]<1):
# #                 print("sensor ID not valid "+str(processData.headersProcess.headers[0]) + '\n' + '--- ')
# #                 
# #                 print("previous packet: ", str(prevPacket))
# #                 print("previous packet Type: ",prevPacketType)
# #                 print("current packet: ", str(valueAll))
#             print("current Packet Type :", processData.headersProcess.type_data)
#             print("current Packet data length :", str(processData.headersProcess.len_data))
#             prevPacket=valueAll
#             prevPacketType=processData.headersProcess.type_data

        def handle_client_connection(self, client_socket):

            self.plc_socket=client_socket
            
            time.sleep(5)

          
            #client_socket.send(self.get_status)

            while True:
                processData = SensorDataProcess()
                self.recv_data(client_socket,processData)
                if(processData.connection_terminated):
                        print("connection is terminated " )
                        self.logger.error("connection is terminated ")
                        self.update_conected_plc("")
                        return 
               # ts = {"ts":SensorDataProcess.current_milli_time()}
                #self.dict_allSensor_by_id[processData.headersProcess.id_sensor] = client_socket
#                 self.update_conected_sensors(self.dict_allSensor_by_id)
#               
#                 if processData.headersProcess.is_plc_data or processData.headersProcess.isRawData :#or self.headersProcess.type_data == "end_of_pac":
# 
#                     id_socket, data = processData.process_data(ts)
# 
#  
#                   
#                     try:
#                         self.user.send_telemetry(id_socket, data, processData.headersProcess.isRawData )
#                         
#                     except Exception as e:
#                         print("error sending data serv" + str(e))
#                 else:
#                     fer = self.function_process_data_to_view(processData)
#                     

#         def send_to_sensor(self, ids_sensor: list, data: str ):
# #             if read_sensor_raw_data_in_secods:
# #                 for i in ids_sensor:
# #                     if i not in self.list_sensors_send_coomend_read_raw_data:
# #                         self.list_sensors_send_coomend_read_raw_data[i] = read_sensor_raw_data_in_secods
#             for i in ids_sensor:
#                 if i not in self.dict_allSensor_by_id:
#                     return 'error id sensor ' + str(i)
#                 try:
#                     self.dict_allSensor_by_id.get(i).send(data)
#                 except Exception as e:
#                     print(e)
#             return ''
        def createLogger(self,loggerName):
           
            
           
            self.logger = logging.getLogger(loggerName)
            handler = RotatingFileHandler('../logs/'+loggerName+'.log', maxBytes=20000000, backupCount=20)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
            
        
                  
 
                
                
                
        def send_to_plc(self, data: str ):
#             if read_sensor_raw_data_in_secods:
#                 for i in ids_sensor:
#                     if i not in self.list_sensors_send_coomend_read_raw_data:
#                         self.list_sensors_send_coomend_read_raw_data[i] = read_sensor_raw_data_in_secods
            
            
            try:
                result =self.plc_client.write_registers(0,[300,305],unit=0X01) 
                print (str(result))
            except Exception as e:
                    print("error sending data to PLC " + str(e))
                    self.logger.error("error sending data to PLC " + str(e))
            
       
              
          

 
#         def ComputeCRC (self,data_send,data_length):
#              
#              GENPOLY = 0xA001
#              accum = 0xFFFF
#  
#              for i in data_send:
#                     #  processes all bytes of string with lenght len
#                 accum = i#( int)(accum ^ (int) data_send[i])    #//  XOR low order byte
#                 for j in range(8):
#                  
#                     if ((accum & 0x0001) != 0):
#                      
#                         accum = (  int)(accum >> 1)
#                         accum = (  int)(accum ^ GENPOLY)
#                      
#                     else :  accum = (  int)(accum >> 1)
#        
#              return accum 


    def __new__(cls) -> __TcpServer:  # __new__ always a classmethod

        if not TcpServPLC.instance:
            TcpServPLC.instance = TcpServPLC.__TcpServer()
        return TcpServPLC.instance
