import tkinter as tk
import time
from tkinter import BooleanVar, Entry,IntVar,ttk
import threading
from properties.PropertiesReader import ConfParams
from ThingBoardConection.client import ThingBoardUser
from Cmd.CmdM import Cmd 
 
from TcpServer.sensorDataProcessing import algoParams
from TcpServer.sensorDataProcessing import SensorDataProcess
#from pepsiN.TcpServer.plcDataProcessing import plcParams

#import ast
#from tkinter import messagebox
import json

#import ast
#from tkinter import messagebox
class CmdView:
    #seconds_of_last_raw_data: Entry
    password: Entry
    SSId: Entry
    init_sensor: BooleanVar
    update_sensor_BIST: BooleanVar
    transmitting_row_data: BooleanVar
    pointer_leaser: BooleanVar
    handle_data_send = None
    
      
    update_sensors_server=None
    params=ConfParams() 

 

    entries = []

    algo_select = ""
    plc_mode_select = ""
 
 
    container=None
    master = tk.Tk()
    canvas=None
    scrollable_frame=None

    algo_params = algoParams()

    algoritem_options = algo_params.algoritem_options


    plc_mode_options="a"
    raw_data_type=algo_params.raw_data_type

    fildes_by_algo = algo_params.params_logic

    check_box_text_and_value = {
        # "rtc": {
        #     "text": "update RTC",
        #     "value": tk.IntVar(),
        # },
        "pointer_leaser": {
            "text": "EU HW:Turn ON Laser pointer",
            "value": tk.IntVar(),
        },
        "transmited_to_gatway": {
            "text": "WI-FI:Transmit PLC parameters",
            "value": tk.IntVar()
        },
        # "init_sensor":{
        #     "text": "init sensor",
        #     "value": tk.IntVar(),
        # },
        # "sensor_bist": {
        #     "text": "update sensor BIST",
        #     "value": tk.IntVar(),
        # } ,
        "transmited_row_data": {
            "text": "WI-FI:Transmit Raw DATA",
            "value": tk.IntVar(),
        }
        
         ,#enablerawdatatouart/disablerawdatatouart
        "print_row_data_to_uart": {
            "text": "UART:Transmit Raw DATA",
            "value": tk.IntVar(),
        }
        
         ,"print_row_data_to_uart_every_minute": {
            "text": "UART:Tr. Raw DATA every minute",
            "value": tk.IntVar(),
            
            
            
        }
         
          ,"print_incoming_packets_info_to_console": {
            "text": "Console: Print incoming packets",
            "value": tk.IntVar(),
            
            
            
        }
    }
  
  
    error_label = None

    updateRTC = None

    id_sensor = [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13]

    params_input_element = []

    check_box_element = []

    prev_algo_select = ""

    port = ""

    ip_server = ""

    id_sensor_field:IntVar

    data = {}

    select_all = 0

    sensor_select = None

    list_bist = ["normal","saw","sinus"]

    option_element = None
    command_file=None

    e1 = None
    
    cal_fac1 = 0
    vt_cal_fac = 0

    def __init__(self, handle_data,update_sensors_server):
        self.handle_data_send = handle_data
        self.update_sensors_server=update_sensors_server
        self.init_view()


    def update_conected_sensors(self,conected_sensors):
        self.connected_sensors_lab.configure (  text="connected sensors: "+str(conected_sensors.keys() ).replace("dict_keys","") )
    
    def update_conected_plc(self,conected_plc):
        self.connected_plc_lab.configure (  text="connected PLC: "+str(conected_plc )  )
        
    def add_bool_to_sender_data(self, file, value):
        if file=="print_incoming_packets_info_to_console":
            self.update_sensors_server("na","print_incoming_packets_info_to_console",bool(value.get()))
        else:
            self.data[file] = value.get()
        # print(self.data)

    def send_cmd(self,addlData=None):
        error_message=None
        if not addlData:
            addlData={}
        try:
            self.data["id"] = self.sensor_select.get() if not self.select_all else 'all'
            
            
            if("get_debug_buffer" in addlData):
                self.data["get_debug_buffer"]=addlData["get_debug_buffer"]
                print(self.data)
                return self.handle_data_send(self.data,False,error_message)
            
            if self.password.get():
                self.data["network_password"] = self.password.get()
    
            if self.SSId.get():
                self.data["network_name"] = self.SSId.get()
    
            
    
            if self.id_sensor_field.get():
                self.data["id_sensor"] = int(self.id_sensor_field.get())
    
            if self.sensor_bist.get():
                self.data["sensor_bist"] = self.list_bist.index(self.sensor_bist.get())
    
            if self.port.get():
                self.data["network_port"] = self.port.get()
                
    #         if self.seconds_of_last_raw_data.get():
    #             self.data["get_raw_data"] = int(self.seconds_of_last_raw_data.get())
    
            if self.ip_server.get():
                self.data["network_server_ip"] = self.ip_server.get()
    #at embedded :  {Algo_2=2,Algo_3_4=3,Algo_5=4,No_Algo=5};
            if self.algo_select.get():
                #self.data["algo_selected"] = self.algoritem_options.index(self.algo_select.get())+2
                self.data["algo_selected"] = self.algoritem_options[self.algo_select.get()]
                #if(self.data["algo_selected"]>2):
                #    self.data["algo_selected"] =  self.data["algo_selected"]+1
                 
                self.data["params"] = []

                for entryIndex in range(len(self.entries)):
                    value=''
                    if (isinstance(self.entries[entryIndex], Entry)):
                        value=self.entries[entryIndex].get()
                    else :
                        value=self.raw_data_type.index(  self.entries[entryIndex].get())+1
                        
                    self.data["params"].append(value)
            
            for key in addlData:
                self.data[key]=addlData[key]
                
        except Exception as e:
            msg=str(e)
            print("general error " + msg)
            error_message="Error while parsing GUI parameters, please verify values are not missing or not correct"
             
        print(self.data)
        return self.handle_data_send(self.data,False,error_message)

    def set_ids(self):
        self.option_element.pack_forget() if self.select_all  else self.option_element.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

    def show_error(self, message):
        self.error_label.config(text=message)

    def clear_params_list(self):
        self.entries = []
        for i in self.params_input_element:
            i.pack_forget()

        if self.data.get("params"):
            del self.data["params"]

   
    
    
    
    def set_params(self):

        self.clear_params_list()
        #index=self.algoritem_options.index(self.algo_select.get())
        key=self.algoritem_options[self.algo_select.get()]
        #if(index>0):
        #    index=index+1
        fildes = self.fildes_by_algo[str(key)]
        
        #No Algo
        #if (index == 3):
        if (key == 5):
            self.set_row_data_options()
            return
        
        #algo_2_demo
        #elif (index == 4):
        elif (key == 6):
            return

        self.option_element.pack_forget()
        for field in range(len(fildes)):
            row = tk.Frame(self.master)
            lab = tk.Label(row, width=15, text=fildes[field], anchor='w')
            ent = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.params_input_element.append(row)
            self.params_input_element.append(lab)
            self.params_input_element.append(ent)
            self.entries.append(ent)

    def set_row_data_options(self):
       
        row = tk.Frame(self.master)
        self.select_row_data_options = tk.StringVar(row)
        # row = tk.Frame(row)
        lab = tk.Label(row, width=15, text="choosing row data type", anchor='w')
        self.row_data_options_list = tk.OptionMenu(row, self.select_row_data_options, *self.raw_data_type)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        self.row_data_options_list.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        
           
        self.params_input_element.append(row)
        self.params_input_element.append(lab)
        self.params_input_element.append(self.row_data_options_list)
        self.entries.append(self.select_row_data_options)


    def get_status(self):
        idS = self.sensor_select.get() if not self.select_all else 'all'
        # self.data["id"] = self.sensor_select.get() if not self.select_all.get() else 'all'
        self.clear_all()
        self.data["id"] = idS
        self.data["status"] = True
        self.handle_data_send(self.data)
        self.data = {}

    def reset_device(self,ids=None):
        if(not ids):
            idS = self.sensor_select.get() if not self.select_all else 'all'
        # self.data["id"] = self.sensor_select.get() if not self.select_all.get() else 'all'
        self.clear_all()
        self.data["id"] = idS
        self.data["reset_eu"] = True
        self.handle_data_send(self.data)
        self.data = {}

    def get_command_file(self):
         
        if not self.sensor_select.get() and not self.select_all:
            self.show_error( 'you must select sensor')
            return
        
        idS = self.sensor_select.get() if not self.select_all else 'all'
        
        
        #self.clear_all()
        
         
        command_file=self.params.getParam("COMMAND_FILE_PATH")#C:/Users/USER/Desktop/Manual/requirements.txt
        # Using readlines() 
        print("open file : "+command_file)
        file1 = open(command_file, 'r') 
        Lines = file1.readlines() 
        file1.close()
                                                               
        for line in Lines:
           
            print("process line : "+str(line)) 
            write_command_length=None
            self.data["id"] = idS
            
            if line[0]=="R":
                splitted = line.split(",")
                #skip 4th number
                line = ",".join(splitted[:4]) + ","+splitted[5]
                line="R26,06,"+line.replace("R", "27", 1)
                indx = int(splitted[1])
                param_type = splitted[4].strip()
                #store param_type by index to be used on reply
                self.update_sensors_server("command",str(indx),param_type)                
                 
            elif line[0]=="r":
                splitted = line.split(",")
                #skip 4th number
                line = ",".join(splitted[:4]) + ","+splitted[5]                
                line="R26,06,"+line.replace("r", "27", 1)
                indx = int(splitted[1])
                param_type = splitted[4].strip()
                self.update_sensors_server("command",str(indx),param_type)                
                             
            elif line[0]=="W":
                
                write_command_length =line.count(',')+2
                splitted = line.split(",")
                #skip 3rd number
                line = ",".join(splitted[:3]) + "," + ",".join(splitted[4:])
                line="W26,"+str(write_command_length)+","+line.replace("W", "26", 1)
                
                 
            elif line[0]=="w":
                 
                write_command_length =line.count(',')+2
                splited = line.split(",")
                #skip 3rd number
                line = ",".join(splitted[:3]) + "," + ",".join(splitted[4:])
                line="W26,"+str(write_command_length)+","+line.replace("w", "26", 1)
                
           
            print("Sent line is ", line)
            self.data["command"]=line
            self.data["send_command"]=True 
            self.handle_data_send(self.data)
            self.data = {}
     
        
    def update_plc_device(self):
        
        # self.data["id"] = self.sensor_select.get() if not self.select_all.get() else 'all'
        # self.clear_all()
#             Buffer[0] = module address                            (0x01);
#             Buffer[1] = function                                  (0x03 '03' Read Multiple Registers); //write 16(decimal)
#             Buffer[2] = Register Address High Byte                (0x038 - add 14468);
#             Buffer[3] = Register Address Low Byte                 (0x084 - add 14468);
#             Buffer[4] = number of word(16 bit) to return MSB      (0x00);
#             Buffer[5] = number of word(16 bit) to return LSB      (0x02 - 2 word to return);
#             Buffer[6] = CRC LOW BYTE                              (0x89);
#             Buffer[7] = CRC HIGH BYTE                             (0x42);
       
        pass
        #self.data["module address"] = 1
        #self.data["function"] = 3
        # self.data["Register Address"] =14468
         
        # self.data["plc data"] =2  
        
       
        #self.handle_data_send(self.data,True)
        # self.data = {}

#     def cb(self, event):
#         print ("variable is"+ self.var.get())
#         self.add_bool_to_sender_data(self.field_text, self.value)
 
    def set_check_box_view(self):

        for key, field in self.check_box_text_and_value.items():
            row = tk.Frame(self.master)
            # self.check_box_text_and_value[field]["value"] = tk.Variable()
            field["value"].set(0)
#              c = Checkbutton(
#             master, text="Enable Tab",
#             variable=self.var,
#             command=self.cb)
            c = tk.Checkbutton(row, text=field["text"], variable=field["value"],command=lambda field_text=key, value=field["value"]: self.add_bool_to_sender_data(field_text, value))
            #tk.Button(row, text='Apply', command=lambda field_text=key, value=field["value"]: self.add_bool_to_sender_data(field_text, value)).pack(side=tk.RIGHT, padx=3, pady=3)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            c.pack(side=tk.LEFT)

    def get_last_raw_data(self):
        idS = self.sensor_select.get() if not self.select_all else 'all'
        # self.data["id"] = self.sensor_select.get() if not self.select_all.get() else 'all'
        self.clear_all()
        self.data["id"] = idS
        self.data["get_raw_data"] = True
        self.handle_data_send(self.data)
        self.data = {}

    def clear_all(self):
        self.data = {}
        for field in self.check_box_text_and_value:
            self.check_box_text_and_value[field]["value"].set(0)

        self.algo_select.set("")
        self.clear_params_list()
        self.SSId.delete(0, 'end')
        self.password.delete(0, 'end')
        self.port.delete(0, 'end')
        self.ip_server.delete(0, 'end')
        self.sensor_select.set("")
        self.select_all=0
        self.id_sensor_field.set("")
        self.sensor_bist.set("")
     
        #self.seconds_of_last_raw_data.delete(0, 'end')
        self.set_ids()

    def init_view(self):

        master = self.master
        master.title(self.params.getParam("GATEWAY_NAME")+' , v:'+self.params.getParam("VERSION"))

        # Change - Start
        tabControl = ttk.Notebook(master)

        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)

        tabControl.add(tab1, text='Main')
        tabControl.add(tab2, text='Config')
        tabControl.add(tab3, text='Calibration')

        tabControl.pack(expand=1, fill="both")
        # Change - End

        #container = ttk.Frame(master)
        self.canvas = tk.Canvas(tab1)
        canvas=self.canvas
        # scrollbar = ttk.Scrollbar(master, orient="vertical", command=canvas.yview)
        scrollbar = ttk.Scrollbar(tab1, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        scrollable_frame= self.scrollable_frame 
      
#         scrollable_frame.bind(
#             "<Configure>",
#             lambda e: canvas.configure(
#                 scrollregion=canvas.bbox("all")
#                 )
#             )
        
        self.master = scrollable_frame
        master = self.master
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw",tags="my_tag")

        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollable_frame.bind("<Configure>", self.OnFrameConfigure)

        self.sensor_select = tk.StringVar()
        row = ttk.Frame(self.scrollable_frame)
        lab = tk.Label(row, width=15, text="select Sensor", anchor='w')
        self.option_element = tk.OptionMenu(row, self.sensor_select, *self.id_sensor)
        c = tk.Checkbutton(row, width=15, text="select all Sensors", variable=self.select_all, command=self.set_ids)

        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        self.option_element.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        c.pack()

        self.set_check_box_view()

        row = ttk.Frame(scrollable_frame)
        lab = tk.Label(row, text="WIFI", anchor='w')
        self.SSId = tk.Entry(row)
        self.password = tk.Entry(row)
       
        lab.pack(side=tk.LEFT)
        self.SSId.pack(side=tk.LEFT, expand=tk.YES)
        self.password.pack(side=tk.LEFT, expand=tk.YES)

        self.port = tk.Entry(row)
        self.ip_server = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        self.port.pack(side=tk.LEFT, expand=tk.YES)
        self.ip_server.pack(side=tk.LEFT, expand=tk.YES)
# 
#         row = ttk.Frame(scrollable_frame)
#         lab = tk.Label(row, text="Write bytes to vz sensor", anchor='w')
#         self.byte_to_sensor = tk.Entry(row)
#         row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
#         lab.pack(side=tk.LEFT)
#         self.byte_to_sensor.pack(fill=tk.X, expand=tk.YES)

#         row = tk.Frame(self.master)
#         lab = tk.Label(row, text="Get the latest data in seconds", anchor='w')
#         self.seconds_of_last_raw_data = tk.Entry(row)
#         row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
#         lab.pack(side=tk.LEFT)
#         self.seconds_of_last_raw_data.pack(fill=tk.X, expand=tk.YES)


        self.id_sensor_field = tk.StringVar(row)
        row = ttk.Frame(scrollable_frame)
        lab = tk.Label(row, width=15,text="Write EU ID:", anchor='w')
        op = tk.OptionMenu(row, self.id_sensor_field, *self.id_sensor)
        
        lab.pack(side=tk.LEFT)
        op.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)

        self.sensor_bist = tk.StringVar(row)
       
        lab = tk.Label(row, width=15,text="Sensor BIST", anchor='w')
        op = tk.OptionMenu(row, self.sensor_bist, *self.list_bist)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        op.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)



        self.algo_select = tk.StringVar()
        row = ttk.Frame(scrollable_frame)
        lab = tk.Label(row, width=15, text="select algo", anchor='w')
        op = tk.OptionMenu(row, self.algo_select, *self.algoritem_options, command=lambda _: self.set_params())
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        op.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        self.plc_mode_select = tk.StringVar()
        row = ttk.Frame(scrollable_frame)
        lab = tk.Label(row, width=15, text="PLC Mode", anchor='w')
        op = tk.OptionMenu(row, self.plc_mode_select, *self.plc_mode_options, command=lambda _: self.update_plc_device())
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        op.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)


        self.error_label = tk.Label(master, fg="red")
        self.error_label.pack(padx=5, pady=5)



  
         
        row = ttk.Frame(scrollable_frame)
        self.connected_sensors_lab = tk.Label(row ,text="connected sensors", anchor='w')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.connected_sensors_lab .pack(side=tk.LEFT)

        row = ttk.Frame(scrollable_frame)
        self.connected_plc_lab = tk.Label(row ,text="connected PLC: ", anchor='w')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.connected_plc_lab .pack(side=tk.LEFT)

        tk.Button(master,
                  text='Get DB', command=self.get_debugge_buffer_packet).pack(side=tk.RIGHT, padx=8, pady=8)

        tk.Button(master,
                  text='VZWrite ', command=self.get_command_file).pack(side=tk.RIGHT, padx=8, pady=8)
                  
        tk.Button(master,
                  text='RD Packet', command=self.get_row_data_packet).pack(side=tk.RIGHT, padx=8, pady=8)
     
        tk.Button(master,
                  text='Status', command=self.get_status).pack(side=tk.RIGHT, padx=8, pady=8)

        tk.Button(master,
                  text='Reset', command=self.reset_device).pack(side=tk.RIGHT, padx=8, pady=8)

        tk.Button(master,
                  text='Clear', command=self.clear_all).pack(side=tk.RIGHT, padx=8, pady=8)

        tk.Button(master,
                  text='SEND', command=self.send_cmd).pack(side=tk.RIGHT, padx=8, pady=8)
               
        # Change - Start
        string_vars = {}
        # the fields must match the saved_config dictionary
        params = {'FWI': 'FWI (Former Wear Indication)',
                  'TCC': 'TCC (Time of Charge Compaction)',
                  'PSD': 'PSD (Product in Seal Detection)',
                  'TBS': 'TBS (Time of Bag Spacing)',
                  'ABH': 'ABH (Average Bag Height)',
                  'TBL': 'TBL (Time of Bag Length)',
                  'CFT': 'CFT (Chips Fall Time)',
                  'JCT': 'JCT (Jaws Cycle Time)'}

        def send_params():
            return_map = {'FIRST_SHIFT': (start_1st_shift.get(), end_1st_shift.get()),
                          'SECOND_SHIFT': (start_2nd_shift.get(), end_2nd_shift.get()),
                          'N': n.get()}

            for token in params.keys():
                return_map[token] = []
                for place in range(5):
                    return_map[token].append(string_vars[token][place].get())

            #print(return_map)

            with open('config.txt', 'w') as outfile:
                json.dump(return_map, outfile)

            params_to_send = {"START_FIRST_SHIFT": start_1st_shift.get(),
                              "END_FIRST_SHIFT": end_1st_shift.get(),
                              "START_SECOND_SHIFT": start_2nd_shift.get(),
                              "END_SECOND_SHIFT": end_2nd_shift.get(),
                              "LAST_N": n.get()}            
            user = ThingBoardUser()
            user.send_attributes("PLC", params_to_send)

        # To Do - add validation
        def valid_time():
            return True

        def prepare_second_table_row(token, desc):
            row = tk.Frame(tab2)
            row.pack(fill=tk.X)

            string_vars[token] = []
            for i in range(5):
                string_vars[token].append(tk.StringVar())

            row_label = tk.Label(row, text=desc, width=30)
            string_vars[token][0].set(saved_config[token][0])
            column_1 = Entry(row, textvariable=string_vars[token][0], width=20)
            string_vars[token][1].set(saved_config[token][1])
            column_2 = Entry(row, textvariable=string_vars[token][1], width=20)
            string_vars[token][2].set(saved_config[token][2])
            column_3 = Entry(row, textvariable=string_vars[token][2], width=20)
            string_vars[token][3].set(saved_config[token][3])
            column_4 = Entry(row, textvariable=string_vars[token][3], width=20)
            string_vars[token][4].set(saved_config[token][4])
            column_sensor = Entry(row, textvariable=string_vars[token][4], width=20)

            row_label.pack(side=tk.LEFT)
            tk.Label(row, width=2, bg="red").pack(side=tk.LEFT)
            column_1.pack(side=tk.LEFT)
            tk.Label(row, width=2, bg="yellow").pack(side=tk.LEFT)
            column_2.pack(side=tk.LEFT)
            tk.Label(row, width=2, bg="LimeGreen").pack(side=tk.LEFT)
            column_3.pack(side=tk.LEFT)
            tk.Label(row, width=2, bg="yellow").pack(side=tk.LEFT)
            column_4.pack(side=tk.LEFT)
            tk.Label(row, width=2, bg="red").pack(side=tk.LEFT)
            column_sensor.pack(side=tk.LEFT)


        def calibration_step_1():
            self.vt_cal_fac = 50
            self.cal_fac = 1
            cal_fac_du2m_s = 2 ** 8 * 1000 * self.cal_fac/self.vt_cal_fac
            self.data["algo_selected"] = self.algoritem_options["algo_8"]
            self.data["id"] = self.sensor_select.get() if not self.select_all else 'all'
            self.data["params"] = []
            print("cal_fac_du2m_s ",cal_fac_du2m_s)
            self.data["params"].append(cal_fac_du2m_s)
            print("self.data ",self.data)
            self.send_cmd()
            time.sleep(5) 

            ref_val = 100
            SensorDataProcess.collect_calibration = True

            def step_1_function():
                print("in Calibration 1")
                message_var.set("Wait a minute to continue")
                mean_val = SensorDataProcess.mean_med_vel
                self.cal_fac1 = mean_val / ref_val
                print("cal_fac1: ", self.cal_fac1)
                message_var.set(
                    "The first test is completed, set the machine to the next velocity and run the second test.")
                button_2['state'] = 'normal'
                button_1['state'] = 'disabled'

            t = threading.Timer(6*10, step_1_function)
            t.start()


        def calibration_step_2():
            ref_val = 200

            SensorDataProcess.collect_calibration = True

            def step_2_function():
                print("in Calibration 2")
                message_var.set("Wait a minute for result")
                mean_val = SensorDataProcess.mean_med_vel
                cal_fac2 = mean_val / ref_val
                cal_fac = (self.cal_fac1 + cal_fac2) / 2
                print("self.cal_fac1: ", self.cal_fac1)
                print("cal_fac2: ", cal_fac2)
                print("cal_fac: ", cal_fac)
                if cal_fac > 0 and abs(self.cal_fac1 - cal_fac2)/ cal_fac < 0.1:
                    cal_fac_du2m_s = 2 ** 8 * 1000 * cal_fac/self.vt_cal_fac
                    message_var.set(
                        "The second test is completed, the Calibration Constant is calculated! \n Calibration Constant = "+str(cal_fac_du2m_s))
                    self.data["algo_selected"] = self.algoritem_options["algo_8"]
                    self.data["id"] = self.sensor_select.get() if not self.select_all else 'all'
                    self.data["params"] = []
                    self.data["params"].append(cal_fac_du2m_s)
                    self.send_cmd()
                else: 
                    message_var.set(
                        "Calculation error: The 'angle factor' of the first and the second runs are not equal!")
                
                button_1['state'] = 'normal'

            t = threading.Timer(6*10, step_2_function)
            t.start()


        # Display configuration part of form
        try:
            with open('config.txt', 'r') as infile:
                saved_config = json.load(infile)
        except Exception:
            saved_config = {'FIRST_SHIFT': ('', ''),
                            'SECOND_SHIFT': ('', ''),
                            'N': '',
                            'FWI': (0, 0, 0, 0, 'VZ4'),
                            'TCC': (0, 0, 0, 0, 'VZ1,2,3'),
                            'PSD': (0, 0, 0, 0, 'VZ5'),
                            'TBS': (0, 0, 0, 0, 'VZ6'),
                            'ABH': (0, 0, 0, 0, 'VZ6'),
                            'TBL': (0, 0, 0, 0, 'VZ6'),
                            'CFT': (0, 0, 0, 0, 'VZ1,2,3'),
                            'JCT': (0, 0, 0, 0, 'VZ5')}
        #print(saved_config)

        # Configuration tab
        tk.Label(tab2, text="Shift change settings", bg="red").pack(fill=tk.X, pady=15)

        top_table = tk.Frame(tab2)
        top_table.pack()

        left_side = tk.Frame(top_table)
        left_side.pack(side=tk.LEFT)

        row11 = tk.Frame(left_side)
        start_1st_shift_label = tk.Label(row11, text="Start of first shift", width=30)
        start_1st_shift = Entry(row11, width=20, validate='key', validatecommand=valid_time)
        start_1st_shift.insert(tk.END, saved_config["FIRST_SHIFT"][0])
        row11.pack(fill=tk.X)
        start_1st_shift_label.pack(side=tk.LEFT)
        start_1st_shift.pack(side=tk.LEFT)

        row12 = tk.Frame(left_side)
        end_1st_shift_label = tk.Label(row12, text="End of first shift", width=30)
        end_1st_shift = Entry(row12, width=20, validate='key', validatecommand=valid_time)
        end_1st_shift.insert(tk.END, saved_config["FIRST_SHIFT"][1])
        row12.pack(fill=tk.X)
        end_1st_shift_label.pack(side=tk.LEFT)
        end_1st_shift.pack(side=tk.LEFT)

        row13 = tk.Frame(left_side)
        row13.pack(fill=tk.X)
        tk.Label(row13, text='', width=30).pack(side=tk.LEFT)
        Entry(row13, width=20, state='disabled').pack(side=tk.LEFT)

        row14 = tk.Frame(left_side)
        n_label = tk.Label(row14, text="N", width=30)
        n = Entry(row14, width=20)
        n.insert(tk.END, saved_config['N'])
        row14.pack(fill=tk.X)
        n_label.pack(side=tk.LEFT)
        n.pack(side=tk.LEFT)

        right_side = tk.Frame(top_table)
        right_side.pack(side=tk.LEFT)

        row21 = tk.Frame(right_side)
        start_2nd_shift_label = tk.Label(row21, text="Start of second shift", width=30)
        start_2nd_shift = Entry(row21, width=20, validate='key', validatecommand=valid_time)
        start_2nd_shift.insert(tk.END, saved_config["SECOND_SHIFT"][0])
        row21.pack(fill=tk.X)
        start_2nd_shift_label.pack(side=tk.LEFT)
        start_2nd_shift.pack(side=tk.LEFT)

        row22 = tk.Frame(right_side)
        end_2nd_shift_label = tk.Label(row22, text="End of second shift", width=30)
        end_2nd_shift = Entry(row22, width=20, validate='key', validatecommand=valid_time)
        end_2nd_shift.insert(tk.END, saved_config["SECOND_SHIFT"][1])
        row22.pack(fill=tk.X)
        end_2nd_shift_label.pack(side=tk.LEFT)
        end_2nd_shift.pack(side=tk.LEFT)

        row23 = tk.Frame(right_side)
        row23.pack(fill=tk.X)
        tk.Label(row23, text='', width=30).pack(side=tk.LEFT)
        Entry(row23, width=20, state='disabled').pack(side=tk.LEFT)

        row24 = tk.Frame(right_side)
        row24.pack(fill=tk.X)
        tk.Label(row24, text='', width=30).pack(side=tk.LEFT)
        Entry(row24, width=20, state='disabled').pack(side=tk.LEFT)

        tk.Label(tab2, text="Data ranges settings", bg="red").pack(fill=tk.X, pady=15)

        row0 = tk.Frame(tab2)
        header = tk.Label(row0, text="Parameter name", width=30, bg="LightGray")
        header1 = tk.Label(row0, text="Limit 1", width=17, bg="LightGray")
        header2 = tk.Label(row0, text="Limit 2", width=17, bg="LightGray")
        header3 = tk.Label(row0, text="Limit 3", width=17, bg="LightGray")
        header4 = tk.Label(row0, text="Limit 4", width=16, bg="LightGray")
        header_sensor = tk.Label(row0, text="Sensor SN", width=17, bg="LightGray")

        row0.pack(fill=tk.X)

        header.pack(side=tk.LEFT)
        tk.Label(row0, width=2, bg="red").pack(side=tk.LEFT)
        header1.pack(side=tk.LEFT)
        tk.Label(row0, width=2, bg="yellow").pack(side=tk.LEFT)
        header2.pack(side=tk.LEFT)
        tk.Label(row0, width=2, bg="LimeGreen").pack(side=tk.LEFT)
        header3.pack(side=tk.LEFT)
        tk.Label(row0, width=2, bg="yellow").pack(side=tk.LEFT)
        header4.pack(side=tk.LEFT)
        tk.Label(row0, width=2, bg="red").pack(side=tk.LEFT)
        header_sensor.pack(side=tk.LEFT)

        for token, desc in params.items():
            prepare_second_table_row(token, desc)

        send = tk.Button(tab2, text="SEND", width=20, command=send_params)
        send.pack(pady=20)

        frame_1 = tk.Frame(tab3, borderwidth = 1)
        frame_1.pack(anchor=tk.W)
        step_1 = tk.Label(frame_1, text="Choose sensor ID on Main tab.\nStep 1: Set Machine to Velocity = 100 m/min and press ENTER, and run test 1: ", width=60, height= 6, font=(None, 12), anchor=tk.W)
        step_1.pack(side=tk.LEFT)
        button_1 = tk.Button(frame_1, text="Test 1", width=10, bd=2, command=calibration_step_1)
        button_1.pack(side=tk.LEFT)
        frame_2 = tk.Frame(tab3, borderwidth = 1)
        frame_2.pack(anchor=tk.W)
        step_2 = tk.Label(frame_2, text="Step 2: Set Machine to Velocity = 200 m/min and press ENTER, and run test 2:", width=60, height= 6, font=(None, 12), anchor=tk.W)
        step_2.pack(side=tk.LEFT, expand=True)
        button_2 = tk.Button(frame_2, text="Test 2", width=10, bd=2, state=tk.DISABLED, command=calibration_step_2)
        button_2.pack(side=tk.LEFT)
        frame_3 = tk.Frame(tab3, borderwidth = 1)
        frame_3.pack(anchor=tk.W)
        step_3 = tk.Label(frame_3, text="Step 3: Wait for calibration constant to be calculated.", width=60, height= 6, font=(None, 12), anchor=tk.W)
        step_3.pack(fill=tk.X, expand=True, anchor="w")
        frame_4 = tk.Frame(tab3, highlightbackground="gray", highlightthickness=1,
                            width=600, height=50)
        frame_4.pack(anchor=tk.W)
        frame_4.pack_propagate(False)
        message_var = tk.StringVar()
        label = tk.Label(frame_4, textvariable=message_var, font=(None, 12))

        # message_var.set("Hey!? How are you doing?")
        label.pack()

        # Change - End

        #dict:
        
    
        # tk.Button(master,
        #           text='get last raw data', command=self.get_last_raw_data).pack(side=tk.RIGHT, padx=8, pady=8)
        #container.pack()
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def displayRawData(self,data):
        data_length=len(data)
        int_data=[]
        for i in range(5, data_length, 2):
            value=int.from_bytes(
                data[i:i + 2], byteorder="big", signed=True)
            int_data.append(value)

        print("Raw Data Packet : "+str(int_data))
        #Display Data
        #messagebox.showinfo("Raw Data",str(data)) 
        
    def update_cmd_view(self,key,value) :
        if key=="raw_data_packet":
            addData={'transmited_row_data': 0}
            self.send_cmd(addData)
            self.displayRawData(value) 

    #for Algo 5
    def get_row_data_packet(self ):
        addData={'transmited_row_data': 1}
        if not self.send_cmd(addData):
            self.update_sensors_server(str( self.data["id"]),"update_view_with_first_raw_data_packet",False)

        sensor_id=self.sensor_select.get() if not self.select_all else 'all'
        self.update_sensors_server(sensor_id,"update_view_with_first_raw_data_packet",True)
    
    def get_debugge_buffer_packet(self ):
      
        # {'get_debug_buffer': DEBUG_BUFFER_TYPE}
        DEBUG_BUFFER_MODE=int(self.params.getParam("DEBUG_BUFFER_MODE"))
        addData={'get_debug_buffer': DEBUG_BUFFER_MODE}
        self.send_cmd(addData)

#         if self.send_cmd(addData)==False:
#             self.update_sensors_server(str( self.data["id"]),"update_view_with_first_raw_data_packet",False)

    def OnFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    @staticmethod
    def run():
        tk.mainloop()

# c = CmdView(15)
# c.run()
