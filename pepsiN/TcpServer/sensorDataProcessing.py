import time
from enum import Enum, auto
from TcpServer.PlcCalculatedParams import  PlcCalculatedParams
from properties.PropertiesReader import ConfParams
#from pywin.framework import startup

class algoParams:
    # at embedded :  {Algo_2=2,Algo_3_4=3,Algo_5=4,No_Algo=5};
    #algoritem_options = ["algo_2", "algo_5", "algo_8", "no_algo","algo_2_demo"]# 0,1,2,3,4,5
    algoritem_options = {"algo_2": 2,
                         "algo_5": 4,
                         "algo_8": 3,
                         "no_algo": 5,
                         "algo_2_demo": 6}# 0,1,2,3,4,5
    #algoritem_options = ["algo_2", "algo_5", "no_algo","algo_2_demo"]# 0,1,2,3,4,5
    raw_data_type =    ["distance only","velocity only"]#"all data",
    #params_logic = [
    #    ["SPC", "Yv_th", "minStartN", "minStopN", "minResult", "VtCoff"],
    #    ["SPC", "th up", "th dn", "swichN", "MaxNBeforeSmPeak", "alpha", "FilterLength",
    #     "AveResultT"],
    #    ["SPC", "Yv_th", "FilterLength", "FilterLengthShort", "SwitchN", "alpha", "DToBelt",
    #     "Error2_th", "Error2_N", "SpikeElimMax", "SpikeElimMin", "SpikeElimMethod", "AutoDToBeltN", "DToBelt_RT5"],
    #    #["CalFacDU2m_s", "V_Thershold_L", "V_Thershold_H", "D_Thershold_L", "D_Thershold_H", "BufferLeng", "NoAccFrames",
    #    # "DistFrameVarTH"],
    #    [],[]
    #]
    params_logic = {
        "2":["SPC", "Yv_th", "minStartN", "minStopN", "minResult", "VtCoff"],
        "4":["SPC", "Yv_th", "FilterLength", "FilterLengthShort", "SwitchN", "alpha", "DToBelt",
         "Error2_th", "Error2_N", "SpikeElimMax", "SpikeElimMin", "SpikeElimMethod", "AutoDToBeltN", "DToBelt_RT5"],
        "3":["CalFacDU2m_s", "V_Thershold_L", "V_Thershold_H", "D_Thershold_L", "D_Thershold_H", "BufferLeng", "NoAccFrames",
         "DistFrameVarTH"],
        "5":[],
        "6":[]
    }

    #paramsOut = [
    #    ["Tcharge","Tcycle_A_2"],
    #    ["ResultT", "NoSmallPeak", "U1Ipoint", "U2Ipoint", "DIpoint", "AveU1Ipoint", "AveU2Ipoint", "AveDIpoint",
    #     "AveResultT" ],
    #    ["Tcycle_A_5", "ChBHight", "ST", "ErrorCode", "DToBelt","TBagSpacing","Tbaglength","SpikesPerLoop"],
    #    #["AccDistHigh", "VelocitySEVec", "AccTime", "StatusFlag"],
    #    [],["algo_2_demo_value"]
    #]
    paramsOut = {
        "2":["Tcharge","Tcycle_A_2"],
        "4":["Tcycle_A_5", "ChBHight", "ST", "ErrorCode", "DToBelt","TBagSpacing","Tbaglength","SpikesPerLoop"],
        "3":["AccDistHigh", "MedVel", "AccTime", "StatusFlag", "DistFrameAv", "DistFrameVar"],
        "5":[],
        "6":["algo_2_demo_value"]
    }

# 4369   ,8738    ,13107,   17476     ,21845
# TCycle,ChBHight,DToBelt,TBagSpacing,TBaglength
# 
# 
# ChBHight,DToBelt-not send to thingsboard

class TypeData(Enum):
    velocity = 0
    distance = auto()
    algo_2 = auto()
    #algo_3_4 = auto()
    algo_8 = auto()
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
    vz_param=auto()# just to promote at Data Type Index
    debuge_buffer=auto()
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
    def is_debuge_buffer(self):
        return self.type_data == "debuge_buffer"

    @property
    def is_vz_param(self):
        return self.type_data == "vz_param"

    @property
    def isRawData(self):
        return self.type_data == "velocity" or self.type_data == "distance"

    @headers.setter
    def headers(self, headers: bytes):
        #print("headers", headers)
        #time.sleep(1)
        self._headers = []

        for i in headers:
            self._headers.append(i)


        try:
            bytes_row_data_length = headers[self.LEN_DATA_INDEX_M:self.LEN_DATA_INDEX_L + 1]

            self.pack_seq_number= self.headers[self.PACKET_SEQ_NUMBER]

            self.len_data = int.from_bytes(bytes_row_data_length, byteorder="big")
            
    
            self.set_type_data()
            
            if self.is_debuge_buffer:
                self.len_data =self.len_data + 1
                self.len_data = 1026 - 1
        except Exception as e:
                    #ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
                print(headers)
                #raise  e
                #if(self.type_data=="algo_5"):
                #    self.len_data =16
                #if(self.headers[self.ID_SENSOR_INDEX]>8 or self.headers[self.ID_SENSOR_INDEX]<1):
                #    print("sensor ID not valid "+str(self.headers) + '\n' + '--- ')

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
    algo_8_ts_diff_list = []
    last_algo_8_ts = 0
    algo_8_data = {}
    first_time_ind = True
    collect_calibration = False
    calibration_list = []
    mean_med_vel = 0
    params = ConfParams()

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

            #return algoParams.paramsOut[data_type_as_number - 2]
            return algoParams.paramsOut[str(data_type_as_number)]
        except Exception as e:
                return []
                print(str(self.headers) + '\n' + '-------------------------------------------------------------')

   
    def get_data_as_decimals (self,value_number_of_byte):
        all_valus=''
        
        start_range = 0
        end_range = self.headersProcess.len_data
        if self.headersProcess.is_debuge_buffer:
            print(" debug buffer index " +str(self.headersProcess.data[0]))
            start_range = 1
            end_range = self.headersProcess.len_data-1
                
        for i in range(start_range, end_range, value_number_of_byte):
            
            #if i==0 and  self.headersProcess.is_debuge_buffer:
            #    print(" debug buffer index " +str(self.headersProcess.data[i]))

            if value_number_of_byte == 2:
                value=int.from_bytes(
                #   self.headersProcess.data[i:i + 2], byteorder="big", signed=True)
                    self.headersProcess.data[i:i + 2], byteorder="big", signed=False)
            else:
                value=int(
                    self.headersProcess.data[i])
                
                 
            all_valus +=   ','+str(value)  
                
        
        all_valus="response of command index: "+all_valus.replace(",", '', 1)
        if not self.headersProcess.is_debuge_buffer:
            all_valus= all_valus.replace(",", ' Data : ', 1)
            
        return all_valus
        
        
        
        
        
    def process_data(self, start_timer=None) -> (str, dict):
        #time.sleep(1)
        plcCalculatedParams=PlcCalculatedParams()
        ts = {"ts": int(round(time.time() * 1000))}
        
        # if start_new_data:
        self.all_data = []
        global first_time_ind
        distance_factor = float(self.params.getParam("ALGO_8_DISTANCE_FACTOR"))
        id_socket = self.id_sensor

        # increment = 1 if self.headersProcess.type_data == "plc_data" else 2

        list_params = self.get_list_params() if self.headersProcess.is_plc_data else None
        iParam=0
        new_obj_to_send = {"ts": ts["ts"], "values": {}}
        self.algo_8_data["TS"] = ts["ts"]
        if(self.headersProcess.isRawData):
            new_obj_to_send=''
        
        if self.headersProcess.type_data == 'algo_8':
            try:
                #AccDistHigh is multiplied by distance_factor
                type_data = list_params[0] if list_params else self.headersProcess.type_data
                value=int.from_bytes(
                    self.headersProcess.data[0:4], byteorder="big", signed=True)
                new_obj_to_send["values"][type_data] = value * distance_factor
                #algo_8_data["TS"] = int(round(time.time() * 1000))
                self.algo_8_data[type_data] = value * distance_factor
         
                type_data = list_params[1] if list_params else self.headersProcess.type_data
                value=int.from_bytes(
                    self.headersProcess.data[4:6], byteorder="big", signed=True)
                new_obj_to_send["values"][type_data] = value
                self.algo_8_data[type_data] = value
         
                type_data = list_params[2] if list_params else self.headersProcess.type_data
                value=int.from_bytes(
                    self.headersProcess.data[6:10], byteorder="big", signed=True)
                new_obj_to_send["values"][type_data] = value
                self.algo_8_data[type_data] = value

                type_data = list_params[3] if list_params else self.headersProcess.type_data
                value=int.from_bytes(
                    self.headersProcess.data[10:11], byteorder="big", signed=True)
                new_obj_to_send["values"][type_data] = value
                self.algo_8_data[type_data] = value

                type_data = list_params[4] if list_params else self.headersProcess.type_data
                value=int.from_bytes(
                    self.headersProcess.data[11:15], byteorder="big", signed=True)
                new_obj_to_send["values"][type_data] = value
                self.algo_8_data[type_data] = value

                type_data = list_params[5] if list_params else self.headersProcess.type_data
                value=int.from_bytes(
                    self.headersProcess.data[15:19], byteorder="big", signed=True)
                new_obj_to_send["values"][type_data] = value
                self.algo_8_data[type_data] = value

                if SensorDataProcess.collect_calibration:
                    SensorDataProcess.calibration_list.append(self.algo_8_data["MedVel"])
                    print(self.calibration_list)
                    if len(SensorDataProcess.calibration_list) > 5:
                        SensorDataProcess.mean_med_vel = sum(SensorDataProcess.calibration_list) / len(SensorDataProcess.calibration_list) 
                        print(SensorDataProcess.mean_med_vel)
                        SensorDataProcess.collect_calibration = False
                        SensorDataProcess.calibration_list = []
   
            except Exception as e:
                print("Error params" + str(self.headersProcess.headers))

            ts_diff = ts["ts"] - SensorDataProcess.last_algo_8_ts
            #print("ts", ts["ts"])
            #print("last_algo_8_ts", SensorDataProcess.last_algo_8_ts)            
            #print("ts_diff", ts_diff)
            new_obj_to_send["values"]["ts_diff"] = ts_diff
            SensorDataProcess.last_algo_8_ts = ts["ts"]
            
            if len(self.algo_8_ts_diff_list) > 99:
                self.algo_8_ts_diff_list.pop(0)
            self.algo_8_ts_diff_list.append(ts_diff)
            #print(self.algo_8_ts_diff_list)
            ts_diff_avg = round(sum(self.algo_8_ts_diff_list) / len(self.algo_8_ts_diff_list))         
            new_obj_to_send["values"]["ts_diff_avg"] = ts_diff_avg
            #Delete first value in run
            #print("first_time_ind ", SensorDataProcess.first_time_ind)
            if SensorDataProcess.first_time_ind:
                self.algo_8_ts_diff_list.pop(0)
                SensorDataProcess.first_time_ind = False
                
        else:
            for i in range(0, self.headersProcess.len_data, 2):
            
                try:
                    type_data = list_params[iParam] if list_params else self.headersProcess.type_data
         
                    #print("type_data :" + str(type_data))
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
                    plcCalculatedParams.set_param(id_socket, type_data,value)       
                    
        self.all_data.append(new_obj_to_send)    
        
        return id_socket, self.all_data
