import time
import  traceback
from TcpServer.sensorDataProcessing import ProcessHeaders, algoParams   


def is_digit(string: str):
    return string.isdigit()


def is_float(string: str):
    try:
        float(string)
        return True
    except ValueError:
        return False


class Cmd:
    algo_selected: int = 0
    processHeaders = ProcessHeaders()

   # read_raw_data_in_seconds = False

    algo_params = algoParams()

    algoritem_options = algo_params.algoritem_options

    params_logic = algo_params.params_logic

    id = None
    data = ""

    data_from_sensor = ""

    def get_value_as_number(self, string_number, type_to_convert):
        if type_to_convert == 'f':
            return float(string_number)
        if type_to_convert == "i":
            return int(string_number)

    def write_data(self, filde, value):

        print("{}: {}\n".format(filde, value))

    def parse_data_from_sensor(self,processData):
        try:
            self.processHeaders=processData.headersProcess
           
            if self.processHeaders.type_data.startswith("network"):
                self.write_data(self.processHeaders.type_data, self.processHeaders.data.decode())
            #at embedded :  {Algo_2=2,Algo_3_4=3,Algo_5=4,No_Algo=5};
            elif self.processHeaders.type_data == "algo_selected":
                self.algo_selected = int.from_bytes(self.processHeaders.data, byteorder="big") 
                #print("if algo_selected ", self.algo_selected)
                if self.algo_selected == 0:
                    self.algo_selected = 2
                elif self.algo_selected == 1:
                    self.algo_selected= 3
                elif self.algo_selected == 2:
                    self.algo_selected= 4
                elif self.algo_selected == 3:
                    self.algo_selected= 5
                elif self.algo_selected == 23:
                    self.algo_selected= 6
                #if( self.algo_selected>0):
                #    self.algo_selected= self.algo_selected-1
                #if( self.algo_selected>3):
                #    self.algo_selected= self.algo_selected-19
                #self.write_data(self.processHeaders.type_data,self.algoritem_options[self.algo_selected])
                for key, value in self.algoritem_options.items():
                    if value == str(self.algo_selected):
                        self.write_data(self.processHeaders.type_data,key)
                    
            elif self.processHeaders.type_data == "params" :
                #params_list_index=self.algo_selected
                if self.algo_selected==1:
                    self.algo_selected = 2
                #   params_list_index=2
                #if self.params_logic[params_list_index]:
                if self.params_logic[str(self.algo_selected)]:
                    #print(self.algoritem_options[self.algo_selected]+" parameters:")
                    for key, value in self.algoritem_options.items():
                        if value == self.algo_selected:
                            print(key+" parameters:")
                    for i in range(0, self.processHeaders.len_data, 2):
                        value = int.from_bytes(self.processHeaders.data[i:i + 2], byteorder="big")
                        #self.write_data("       "+self.params_logic[params_list_index][int(i / 2)], value)
                        #print(str(self.algo_selected))
                        #print(int(i / 2))
                        self.write_data("       "+self.params_logic[str(self.algo_selected)][int(i / 2)], value)
                                        
            elif (self.processHeaders.type_data=="sw_version"):
               
                value= chr(self.processHeaders.data[0])
                iValue=self.processHeaders.data[1]
                if(iValue<10):
                    value=value+"0"
                 
                value=value+str(iValue)
                
                self.write_data(self.processHeaders.type_data, value)
            else:
                value = int.from_bytes(self.processHeaders.data, byteorder="big")
                self.write_data(self.processHeaders.type_data, value)

        # print(self.data_from_sensor)
        except Exception as e:
            print("error parsing data from Sensor " + str(e))
            print( traceback.format_exc())
       
        return self.data_from_sensor

    def convert_to_chars(self,data):
        self.data = ""

        for i in data:
            self.data += chr(i)
#dict: {'transmited_row_data': 0, 'print_row_data_to_uart': 1, 'print_row_data_to_uart_every_minute': 1}
    def pars_cmd(self, data):
        if('print_row_data_to_uart_every_minute' in data and data['print_row_data_to_uart_every_minute']==1):
            data[ 'print_row_data_to_uart']=2
            del data['print_row_data_to_uart_every_minute']
            
            
        data_send = bytes()
        self.id = data.get("id")
        del data["id"]
        if not self.id:
            return 'you must select sensor'
        message_error = ""
     
        
        
        
        if  "send_command" in data:
                command=data["command"]
                command_array=str(command).split(',')
                if command_array[0].startswith("R"):
                    command_array[5]="ADDRESS:"+command_array[5]
                    command_array[0]=command_array[0].replace("R","",1)
                else:
                    command_array[4]="ADDRESS:"+command_array[4]
                    command_array[0]=command_array[0].replace("W","",1)
#                 address=line_array[3]
#                 address_bites=int(address).to_bytes(length=2, byteorder="big")
#                line_array[3]=str(address_bites)
                 
                
                for x in command_array:
                    if x.startswith("ADDRESS:"):
                        temp=x.replace("ADDRESS:","",1)
                        temp=int(temp)
                        data_send+=temp.to_bytes(length=2, byteorder="big")
                    else : 
                        data_send+=int(x).to_bytes(length=1, byteorder="big")
                        
                        
                    
                    
                self.data = data_send
                return message_error
    
        if('algo_selected' in data) :
            #case of No_Algo
            if(data['algo_selected'] ==5):
                if(data['params'][0]==1):
                    data_send=b'\n\x02\x05\x01'
                elif (data['params'][0]==2):
                    data_send=b'\n\x02\x05\x02'
                    
                    
            #case of algo_2_demo        
            elif(data['algo_selected'] ==6):
                    data_send=b'\n\x02\x19'
                     
             
            if  (data_send!=b'') :
                self.data = data_send            
                return message_error
             
                
                
                
        
        for i in data:
#             if i == "get_raw_data":
#                 self.read_raw_data_in_seconds = {"ts":int(round(time.time() * 1000))}
#             if i=="Register Address":
#                 field = data[i].to_bytes(length=2, byteorder="big")
#             elif i=="module address":
#                 field = data[i].to_bytes(length=1, byteorder="big")    
#             elif i=="function":
#                 field = data[i].to_bytes(length=1, byteorder="big")     
#        
#             elif i=="plc data":
#                 field = data[i].to_bytes(length=4, byteorder="big")
           
            if i == "get_debug_buffer" :
                data_send =b'\x1B\x01'
                data_send+= data["get_debug_buffer"].to_bytes(1, byteorder='big') 
                self.data = data_send
                return message_error
          
            elif i == "rtc":
                field = (int(round(time.time() * 1000))).to_bytes(length=6, byteorder="big")
                field = self.processHeaders.set_headers_to_sensor(i, field)
            elif i == "network_name" or i == "network_password" or i == "network_port" or i == "network_server_ip":
                field = data[i].encode()
                field = self.processHeaders.set_headers_to_sensor(i, field)

            elif i == 'params':
                field = bytes()
                if not data["params"]:
                    del data["params"]
                else:
                    for d in data["params"]:
                        d = d if d else -1
                        field += int(d).to_bytes(length=2, byteorder="big",signed=True)
                    field = self.processHeaders.set_headers_to_sensor(i, field)
            else:
                field = data[i].to_bytes(length=1, byteorder="big")
                field = self.processHeaders.set_headers_to_sensor(i, field)
            data_send += field
            # if data[i]:
            #     if self.fields.get(i) and not self.fields[i]["funcValidate"](data[i]):
            #         message_error += "{} value '{}' not valid \n".format(i, data[i])
            #         continue
        # print(len(data_send))
        # self.convert_to_chars(data_send)
        self.data = data_send
        # print(self.data)
        # print(len(self.data))

        return message_error
