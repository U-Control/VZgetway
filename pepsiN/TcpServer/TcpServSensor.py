  
import socket
import traceback
import threading
import struct
from .sensorDataProcessing import * 
from ThingBoardConection.client import ThingBoardUser
import logging
from logging.handlers import RotatingFileHandler
from properties.PropertiesReader import ConfParams
from collections import defaultdict
import time
import decimal
from TcpServer.PlcCalculatedParams import  PlcCalculatedParams
 



class TcpServSensor: 
    instance = None
   
    class __TcpServer:
        params=ConfParams()
        get_status = b'\x12\x01\x01'

        begin_of_packet =b'UUUU'
        user = ThingBoardUser()
        
        plcCalculatedParams= PlcCalculatedParams()
        function_process_data_to_view = None
        update_conected_sensors = None
        update_cmd_view=None
        bind_ip = '0.0.0.0'
        bind_port =  int( params.getParam("GATEWAY_PORT"))
        dict_allSensor_by_id = {}
        # dict_allSockets_by_sensor_id={}
        prevPacket=None 
        prevPacketType=None 
        errorLoggers={} 
        lastPackets={}
        lostPacketsCounter={}
        nextDeviceIdIndexToProcess=0
        generalLogger= None 
        do_update_sensor_server_print_Consol=False
        threadData = threading.local()
        #dataPerSensor={}
        dataPerSensor=defaultdict(dict)
        def getLogger(self,sensor_id):
            logger=None
            if(sensor_id in self.errorLoggers):
                logger=self.errorLoggers[sensor_id]
             
            if(logger != None):
                return logger
            logger = logging.getLogger(sensor_id)
            handler = RotatingFileHandler('../logs/'+sensor_id+'.log', maxBytes=20000000, backupCount=20)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            
            logger.addHandler(handler) 
            logger.setLevel(logging.DEBUG)
            self.errorLoggers[sensor_id]=logger
            return logger
            
            
        def update_sensors_server (self,sensor_id ,key,value):
            if key=="get_debug_buffer":
                
                self.dataPerSensor[sensor_id]["get_debug_buffer"]=value
                
            elif key=="update_view_with_first_raw_data_packet":
                #self.dataPerSensor[sensor_id]="update_view_with_first_raw_data_packet"
                self.dataPerSensor[sensor_id]["update_view_with_first_raw_data_packet"]=value
                #self.threadData.update_view_with_first_raw_data_packet=value
            elif key=="print_incoming_packets_info_to_console":
                self.do_update_sensor_server_print_Consol=value 
            else  : 
                self.dataPerSensor[sensor_id][key]=value
               
               
        def recv_data(self, client_socket,processData):
            #value=client_socket.recv(100)
            #print("first 100 bytes : ", str(value))
            global prevPacket
            global prevPacketType
              
            value=None  
            foundPacketPrefix=False
            # value=client_socket.recv(2000)
            # print("out of reading sync , next 2000: ", value ) 
            #value=client_socket.recv(20000)
            #in case out of reading sync, clearing the socket buffer
            outOfReadingSync=''
            while (not foundPacketPrefix):
                while(value!=b'U'):
                    if(value!= None):
                        outOfReadingSync=outOfReadingSync+str(value)
                    
                    value=client_socket.recv(1)
                    #if(value== b''):
                        #processData.connection_terminated=True
                        #return
                    #print("out of reading sync , next 200: ", str(value)) 
                value=client_socket.recv(4)
                #if(value== b''):
                    #processData.connection_terminated=True
                    #return
                if (value == self.begin_of_packet):
                    foundPacketPrefix=True
                    if(outOfReadingSync!='' and self.do_update_sensor_server_print_Consol):
                        print("out of reading sync")#: ", str(outOfReadingSync))
                    outOfReadingSync=''
                    
                else:
                    value=None  
                 
                   
            value=client_socket.recv( processData.headersProcess.LENGTH_HEADERS)
            #print("headers : ", str(value))
            value_length=len(value)
            while value_length < processData.headersProcess.LENGTH_HEADERS :
                self.generalLogger.warn ("in value.length < processData.headersProcess.len_data loop , length requred"+str(processData.headersProcess.LENGTH_HEADERS)+" and , value "+ str(value))

                value +=client_socket.recv( processData.headersProcess.LENGTH_HEADERS-value_length)
                value_length=len(value)
                   
            #if(value== b''):
                #processData.connection_terminated=True
                #return
                    
            valueAll=value
            processData.headersProcess.headers = value
            #print("headers : ", str(value))
            
            value = client_socket.recv(processData.headersProcess.len_data)
            value_length=len(value)
            while value_length < processData.headersProcess.len_data :
                if self.do_update_sensor_server_print_Consol:
                    self.generalLogger.warning("in value.length < processData.headersProcess.len_data loop , length requred"+str(processData.headersProcess.len_data)+" and , value "+ str(value))
                value +=client_socket.recv( processData.headersProcess.len_data-value_length)
                value_length=len(value)
                
            # if(value== b''):
            #   processData.connection_terminated=True
            #   return
            
            processData.headersProcess.data =  value
            
            
          
            
            valueAll=valueAll+value;
            if  processData.headersProcess.isRawData ==True :
                print("Raw Data :"+str(value))
            logger= self.getLogger(str(processData.headersProcess.headers[0]))
            
            if self.do_update_sensor_server_print_Consol:
                print("PfS :"+str(processData.headersProcess.headers[0])+  " ,SqN : "+ str(processData.headersProcess.headers[4])+" ,Packet Type :", processData.headersProcess.type_data )
            
            if(  processData.headersProcess.is_debuge_buffer    ):
                print("packet data: "+ processData.get_data_as_decimals(2))

            if processData.headersProcess.is_vz_param :
                
                index = str(processData.headersProcess.data[0])
                #print('\nReceived index:', index)
                #print(self.dataPerSensor['command'])
                param_type=int(self.dataPerSensor['command'][index])
                #print('param_type: ', param_type)
                #print('Received data bytes ', str(processData.headersProcess.data))
                  
                if param_type == 1:   # boolean
                    value = struct.unpack('<4B', processData.headersProcess.data[1:])
                elif param_type == 2:   # uint
                    (value,) = struct.unpack('<I', processData.headersProcess.data[1:])
                elif param_type == 3:   # int
                    (value,) = struct.unpack('<i', processData.headersProcess.data[1:])
                elif param_type == 4:    # flout (double)
                    (value,) = struct.unpack('<f', processData.headersProcess.data[1:])
                else:
                    value = struct.unpack('<4B', processData.headersProcess.data[1:])
                    #value = processData.headersProcess.data[1:]
                    #value = processData.get_data_as_decimals(1)
               
                print("packet data: response of command index: ", index, " Data:  ", str(value), '\n')

                
            #PfS :1, SqN: 42, id_sensor: 1
            if(processData.headersProcess.headers[0]>13 or processData.headersProcess.headers[0]<0):
                msg= "sensor ID "+str(processData.headersProcess.headers[0]) +" is not valid, packet content: :"+ str(valueAll) 
                print(msg)
                self.generalLogger.error(msg)
                raise Exception(msg)
            
            lastPacket=None
            sSensorID=str(processData.headersProcess.headers[0])
            if (sSensorID in self.lastPackets):
                lastPacket=self.lastPackets[sSensorID]
                
            if(lastPacket != None):
                currentSeqNumber=processData.headersProcess.headers[4]
                
                lastPackeSeqNumber=lastPacket.headersProcess.headers[4]
                if(   currentSeqNumber!=(lastPackeSeqNumber+1)  and currentSeqNumber!=0 and lastPackeSeqNumber!=255 ):
                    lostCounter=0
                    if (sSensorID in self.lostPacketsCounter):
                        lostCounter=self.lostPacketsCounter[sSensorID]
                    
                    lostCounter=lostCounter+(currentSeqNumber-lastPackeSeqNumber)
                    self.lostPacketsCounter[sSensorID] =lostCounter                  
                    
                    
                    logger.error("lost packets , current seq id  : "+ str(currentSeqNumber) + ' , prev seq ID : '+str(lastPackeSeqNumber))
                    logger.error("lost packets Counter : "+str(lostCounter))
                    logger.error("current packet content  : "+ str(valueAll ))
                    logger.error("prev packet content  : "+  str(processData.headersProcess.headers)+str(processData.headersProcess.data) )
            
            #valdation of algo_2_demo , value --8
            if( processData.headersProcess.headers[3]==25 and  processData.headersProcess.data[1]!=8):
                    logger.error("validation of algo_2_demo value==8 failed, actual value : "+ processData.headersProcess.data[1])
                    logger.error(" packet content  : "+ str(valueAll ))
              
                
            self.lastPackets[sSensorID]=processData
            #print("current Packet data length :", str(processData.headersProcess.len_data))
            #print("current Packet input   :",  valueAll )
            prevPacket=valueAll
            prevPacketType=processData.headersProcess.type_data
            
            sensor_id=str(processData.headersProcess.headers[0])
            
            if sensor_id in self.dataPerSensor and "update_view_with_first_raw_data_packet" in  self.dataPerSensor[sensor_id] and  self.dataPerSensor[sensor_id]["update_view_with_first_raw_data_packet"]==True :#and processData.headersProcess.type_data in ['velocity','distance']   :
                self.update_cmd_view("raw_data_packet",valueAll)
                self.dataPerSensor[sensor_id]["update_view_with_first_raw_data_packet"]=False

        def handle_client_connection(self, client_socket):
  
            
            self.threadData.update_view_with_first_raw_data_packet=False
            time.sleep(5)

            client_socket.send(self.get_status)

            
            while True:
                try:
                    processData = SensorDataProcess()
                    self.recv_data(client_socket,processData)
                    if(processData.connection_terminated):
                        temp_id=None
                        temp_id=processData.headersProcess.id_sensor
                        if id==None:
                            temp_id="" 
                        print("connection is terminated "+ str(temp_id))
                        self.generalLogger.error("connection is terminated "+ str(temp_id))
                        if(temp_id!="" and temp_id in self.dict_allSensor_by_id):
                            del self.dict_allSensor_by_id[temp_id]
                            self.update_conected_sensors(self.dict_allSensor_by_id)  
                        return 
                     
                    ts = {"ts":int(round(time.time() * 1000))}
    #                 if(processData.headersProcess.id_sensor in  self.dict_allSensor_by_id):
    #                     del   self.dict_allSockets_by_sensor_id[self.dict_allSensor_by_id[processData.headersProcess.id_sensor]]
                    self.dict_allSensor_by_id[processData.headersProcess.id_sensor] = client_socket
                    #  self.dict_allSockets_by_sensor_id[client_socket] = processData.headersProcess.id_sensor 
                    self.update_conected_sensors(self.dict_allSensor_by_id)
                    if(  processData.headersProcess.is_debuge_buffer or  processData.headersProcess.is_vz_param):
                        continue
                    if processData.headersProcess.is_plc_data or processData.headersProcess.isRawData :#or self.headersProcess.type_data == "end_of_pac":
    
                        id_socket, data = processData.process_data(ts)
    
     
                      
                        try:
                            
                            do_send_is_alive_ping=(processData.headersProcess.isRawData and processData.headersProcess.pack_seq_number%100==0)
                            self.user.send_telemetry(id_socket, data, processData.headersProcess.isRawData,processData.headersProcess.data,processData.headersProcess.type_data,do_send_is_alive_ping )
                            
                        except Exception as e:
                            print("error sending data serv " + str(e))
                            self.generalLogger.error("error sending data serv " + str(e))
                    else:
                        fer = self.function_process_data_to_view(processData)
               
                except Exception as e:
                    #ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
                    msg=str(e)
                    print("general error " + msg)
                    self.generalLogger.error(msg)
                 
                        
                    print( traceback.format_exc())
                
                    self.generalLogger.error("general error " + str(e)+" processData.headersProcess._headers:  "+ str(processData.headersProcess._headers))
                    self.generalLogger.error("general error   processData.headersProcess._headers:  "+ str(processData.headersProcess._headers))
                    self.generalLogger.error("general error  processData.headersProcess._headers:  "+ str(processData.headersProcess.data))
                    self.generalLogger.error( traceback.format_exc())
                    if( "closed" in msg):
                        return
         
#          
#         def handle_client_connections(self):
# 
#            
#           
#             while True:
#                 sensor_ids=self.dict_allSensor_by_id.keys()
#                 for sensor_id in sensor_ids:
#                     try:
#                         client_socket=self.dict_allSensor_by_id[sensor_id]
#                         self.handle_client_connection(client_socket)
#                     except Exception as e:
#                         print("error sending data serv" + str(e))
#                         self.generalLogger.error("error sending data serv" + str(e))
                   

        def send_to_sensor(self, ids_sensor: list, data: str ):
#             if read_sensor_raw_data_in_secods:
#                 for i in ids_sensor:
#                     if i not in self.list_sensors_send_coomend_read_raw_data:
#                         self.list_sensors_send_coomend_read_raw_data[i] = read_sensor_raw_data_in_secods
            for i in ids_sensor:
                if i not in self.dict_allSensor_by_id:
                    return 'error id sensor ' + str(i)
                try:
                    print("send to sensor "+str(i)+" : "+str(data))
                    self.dict_allSensor_by_id.get(i).send(data)
                except Exception as e:
                    print(e)
                    self.generalLogger.error("error sending data sensor" + str(e))
            return ''

        def run(self):
            if(self.generalLogger==None):
                self.generalLogger=self.getLogger ('generalSensorsGateway')
            
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #server = socket.socket(socket.AF_INET, socket.SOCK_RAW )
           
            server.bind((self.bind_ip, self.bind_port))
            server.listen(8)  # max backlog of connections
            #   print('Listening on {}:{}'.format(self.bind_ip, self.bind_port))
            while True:
                print('Waiting for Sensors connection')
                client_sock, address = server.accept()
                client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF,
                                     10000)
                print('Accepted connection from {}:{}'.format(address[0], address[1]))
                client_handler = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client_sock,))
                client_handler.start()

    def __new__(cls) -> __TcpServer:  # __new__ always a classmethod

        if not TcpServSensor.instance:
            TcpServSensor.instance = TcpServSensor.__TcpServer()
        return TcpServSensor.instance
