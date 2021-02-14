import time
from enum import Enum, auto


class plcParams:
    # at embedded :  {Algo_2=2,Algo_3_4=3,Algo_5=4,No_Algo=5};
   plc_mode_options = ["Mode 1", "Mode 2", "Mode 3" ]# 0,1,2,3,4
  
# 4369   ,8738    ,13107,   17476     ,21845
# TCycle,ChBHight,DToBelt,TBagSpacing,TBaglength
# 
# 
# ChBHight,DToBelt-not send to thingsboard

class TypeData(Enum):
    velocity = 0
    distance = auto()
    algo_2 = auto()
    algo_3_4 = auto()
    algo_5 = auto()
    no_algo = auto()
    pointer_leaser = auto()
    transmited_to_gatway = auto()
    sensor_bist = auto()
    rtc = auto()
    algo_selected = auto()
    params = auto()
    network_name = auto()
    network_password = auto()
    network_port = auto()
    network_server_ip = auto()
    id_sensor = auto()
    transmited_row_data = auto()
    status = auto()
    bytes_from_sensor = auto()
    get_raw_data = auto()
    turn_on = auto()
    print_row_data_to_uart = auto()
    sw_version= auto() 
    reset_eu=auto()
    algo_2_demo=auto()
    end_of_pac = 255

# P_POINTER_LEASER = 6,
#     P_TRANSMITED_TO_GATWAY,//7
#     P_SENSOR_BIST,          //8
#     P_RTC_UPDATE,           //9
#     P_ALGO_SELECTED,        //10  0x0A
#     P_PARAMS,               //11  0x0B
#     P_NET_NAME,             //12  0x0C
#     P_NET_PASS,             //13  0x0D
#     P_NET_PORT,             //14  0x0E
#     P_NET_IP,               //15  0x0F
#     P_ID_SENSOR,            //16  0x10
#     P_TRANSMITED_ROW_DATA,  //17  0x11
#     P_STATUS,               //18  0x12
#     P_BYTES_FROM_SENS,      //19  0x13
#     P_GET_RAW_DATA,         //20  0x14
#     P_TURN_ON,              //21  0x15
#     P_PRINT_RAW_DATA_To_Uart,//22 0x16
#     P_SW_VERS,               //0x17
#     P_END_PAC = 255,
    
class ProcessHeaders:
   

   
    len_data: int
    _headers = []

    ID_SENSOR_INDEX = 0

    LEN_DATA_INDEX_M = 1

    LEN_DATA_INDEX_L = 2

    TYPE_DATA = 3

    PACKET_SEQ_NUMBER = 4
    
    LENGTH_HEADERS = 5

    LENGTH_PACKET_PREFIX = 5
    type_data = ""
    
    pack_seq_number: int
    
    data: bytes = None

    @property
    def id_sensor(self):
        return self.headers[self.ID_SENSOR_INDEX]

    @property
    def headers(self):
        return self._headers

    @property
    def is_plc_data(self):
        return (TypeData[self.type_data].value < 5 and TypeData[self.type_data].value > 1) or TypeData[self.type_data].value==25

    @property
    def isRawData(self):
        return self.type_data == "velocity" or self.type_data == "distance"

    @headers.setter
    def headers(self, headers: bytes):
        # print("headers", headers)
        #time.sleep(1)
        self._headers = []

        for i in headers:
            self._headers.append(i)

        bytes_row_data_length = headers[self.LEN_DATA_INDEX_M:self.LEN_DATA_INDEX_L + 1]

        self.pack_seq_number= self.headers[self.PACKET_SEQ_NUMBER]
        
        self.len_data = int.from_bytes(bytes_row_data_length, byteorder="big")

        self.set_type_data()
        if(self.id_sensor>9):
            print("self.id_sensor>9")
        #if(self.type_data=="algo_5"):
           # self.len_data =16
#         if(self.headers[self.ID_SENSOR_INDEX]>8 or self.headers[self.ID_SENSOR_INDEX]<1):
#             print("sensor ID not valid "+str(self.headers) + '\n' + '--- ')

    def set_type_data(self):
        try:
            self.type_data = TypeData(self.headers[self.TYPE_DATA]).name
        except Exception as e:
            print(str(self.headers) + '\n' + '-------------------------------------------------------------')

    def set_headers_to_sensor(self, i, filde):
        return TypeData[i].value.to_bytes(1, byteorder='big') + (len(filde)).to_bytes(1, byteorder='big') + filde

   


class SensorDataProcess:
    headersProcess = None
    connection_terminated=False
    all_data = None

    def __init__(self ):
        self.headersProcess = ProcessHeaders()
        self.all_data = []
       
       
       
    @property
    def id_sensor(self):
        return self.headersProcess.headers[self.headersProcess.ID_SENSOR_INDEX]

    def get_list_params(self):
        try:
            data_type_as_number = TypeData(self.headersProcess.headers[self.headersProcess.TYPE_DATA]).value
           
            #case it's algo_2_demo 
            if(data_type_as_number==25):
                data_type_as_number=6
            
            return ""
        except Exception as e:
                return []
                print(str(self.headers) + '\n' + '-------------------------------------------------------------')

    def process_data(self, start_timer=None) -> (str, dict):
        #time.sleep(1)
      
        ts = {"ts": int(round(time.time() * 1000))}
       
        # if start_new_data:
        self.all_data = []

        id_socket = self.id_sensor

        # increment = 1 if self.headersProcess.type_data == "plc_data" else 2

        list_params = self.get_list_params() if self.headersProcess.is_plc_data else None
       
        
        iParam=0
        new_obj_to_send = {"ts": ts["ts"], "values": {}}
        if(self.headersProcess.isRawData):
            new_obj_to_send=''
            
        for i in range(0, self.headersProcess.len_data, 2):
           

            try:
                type_data = list_params[iParam] if list_params else self.headersProcess.type_data
               # print("type_data :" + str(type_data))
                iParam=iParam+1
            except Exception as e:
                print("Error params" + str(self.headersProcess.headers))
            value=int.from_bytes(
                self.headersProcess.data[i:i + 2], byteorder="big", signed=True)
            #print(type_data+" : "+str(value))
            # if not Algo Params with no values *"-1")
            if(self.headersProcess.isRawData):
                new_obj_to_send +=  str(self.headersProcess.id_sensor)+','+str(value) + ',\n'
                
            elif (not(self.headersProcess.is_plc_data and  value==-1)):
                new_obj_to_send["values"][type_data] = value
                
       
        
        self.all_data.append(new_obj_to_send)    
        
        return id_socket, self.all_data
