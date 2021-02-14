'''
Created on 18 Aug 2020

@author: USER
'''

import json
from statistics import median
import threading
import datetime
import time
from typing import Dict, Any

from ThingBoardConection.client import ThingBoardUser
from properties.PropertiesReader import ConfParams
from pymodbus3.client.sync import ModbusTcpClient


#  paramsOut = [
#         ["Tcharge","Tcycle_A_2"],
#         ["ResultT", "NoSmallPeak", "U1Ipoint", "U2Ipoint", "DIpoint", "AveU1Ipoint", "AveU2Ipoint", "AveDIpoint",
#          "AveResultT" ],
#         ["Tcycle_A_5", "ChBHight", "ST", "ErrorCode", "DToBelt","TBagSpacing","Tbaglength","SpikesPerLoop"],
#         [],["algo_2_demo_value"]


class PlcCalculatedParams:
    instance = None

    # result =client.read_holding_registers(0,5,unit=0X01)
    # result =client.write_registers(0,[300,305],unit=0X01)

    class __CalculatedParams:

        params = ConfParams()
        user = ThingBoardUser()
        dt2 = 1 / 6000
        TMS_DL = float(params.getParam("INITIAL_TMS_DL"))
        CFT = 0

        TCC_MODE = params.getParam("TCC_MODE")
        TCC = float(params.getParam("INITIAL_TCC"))
        alpha0 = int(params.getParam("IIR_Alfa"))
        dict_Tcycle_A_2_by_sensor_id = {}
        dict_Tcharge_by_sensor_id = {}
        timer = None
        plc_client = None
        if len(params.getParam("PLC_HOST")) > 1:
            plc_client = ModbusTcpClient(params.getParam("PLC_HOST"))

        # after 30 seconds, "hello, world" will be printed
        # a time counter will be more than “TMS” or the time counter will be more than 5 sec

        def init_timer(self):
            # print("init_timer:"+str(self.TMS))
            min_interval = min(5.0, float(self.TMS_DL))
            self.timer = threading.Timer(min_interval, self.timerFunction)
            self.timer.start()

        def timerFunction(self):
            self.submit_CFT_and_TCC()
            # print("sent by Timer, TMS:"+str(self.TMS))

        def set_param(self, sensor_id, param_name, value):
            if self.timer == None:
                self.init_timer()

            if (not param_name):
                return

            if (param_name == "Tcycle_A_2"):
                self.process_Tcycle_A_2(sensor_id, value)

            elif (param_name == "Tcharge"):
                self.process_Tcharge(sensor_id, value)

            elif (param_name == "TBagSpacing"):
                self.submit_parameter("TBS", 0.01 * value, 3)

            elif (param_name == "ChBHight"):
                self.submit_parameter("ABH", 0.1 * value, 4)

            elif (param_name == "Tbaglength"):
                self.submit_parameter("TBL", 0.01 * value, 5)

        def submit_parameter(self, out_param_name, value, plc_reg_address=None):
            ts = {"ts": int(round(time.time() * 1000))}

            # if start_new_data:
            data = []

            new_obj_to_send = {"ts": ts["ts"], "values": {}}

            # Lior process out_param_name ,value
            # Change - Start
            attr_to_send = calculate_info(out_param_name, value)
            #print(value_storage)
            #print(attr_to_send)
            self.user.send_attributes("PLC", attr_to_send)
            
            # new_obj_to_send["values"][out_param_name] = value
            new_obj_to_send["values"][out_param_name] = add_color_digit(value, out_param_name)
            # Change - End

            data.append(new_obj_to_send)
            value = int(value * pow(2, 9))
            try:
                try:
                    if not self.plc_client == None:
                        result = self.plc_client.write_registers(plc_reg_address, [value], unit=0X01)
                        print(out_param_name + " Sent to PLC : " + str(value))
                        self.sendIsAlive()
                except Exception as e:
                    print("error sending data to PLC :  " + str(e))

                self.user.send_telemetry("PLC", data, False, None, None)

            except Exception as e:
                print("error sending data to Things Board :  " + str(e))
                # self.generalLogger.error("error sending data serv " + str(e))

        def process_Tcycle_A_2(self, sensor_id, value):
            self.dict_Tcycle_A_2_by_sensor_id[sensor_id] = value
            if (len(self.dict_Tcycle_A_2_by_sensor_id) == 3 and len(self.dict_Tcharge_by_sensor_id) == 3):
                self.submit_CFT_and_TCC()

        def process_Tcharge(self, sensor_id, value):
            self.dict_Tcharge_by_sensor_id[sensor_id] = value
            if (len(self.dict_Tcycle_A_2_by_sensor_id) == 3 and len(self.dict_Tcharge_by_sensor_id) == 3):
                self.submit_CFT_and_TCC()

        def sendIsAlive(self):
            data = {"ts": int(round(time.time() * 1000)), "values": {"is_alive": True}}
            jsonData = json.dumps(data)
            re = self.user.post(self.user.telemetry_url.format(self.user.access_token("MODBUS")), jsonData)

        def submit_CFT_and_TCC(self):
            if not self.timer == None:
                self.timer.cancel()

            if (len(self.dict_Tcycle_A_2_by_sensor_id) == 0 and len(self.dict_Tcharge_by_sensor_id) == 0):
                # print("no values to be sent by timer, init_timer")
                self.init_timer()
                return

            Nsyc = 0
            ATsycle = 0
            self.CFT = 0

            for value in self.dict_Tcycle_A_2_by_sensor_id.values():

                if (value > 2800 and value < 18000):
                    ATsycle += value
                    Nsyc += 1

            if Nsyc:
                ATsycle = ATsycle / Nsyc
                self.TMS_DL = (float(((10000 - (float(self.alpha0))) * (float(self.TMS_DL)) + (float(self.alpha0)) * (
                    float(ATsycle))) / 10000))
                # self.TMS = self.dt2*float(self.TMS_DL)

            Nsyc = 0
            Tcharge_values_list = []
            if self.TCC_MODE == '0':
                for value in self.dict_Tcharge_by_sensor_id.values():

                    if (value > 0 and value < self.TMS_DL):
                        Tcharge_values_list.append(int(value))
                    else:
                        Tcharge_values_list.append(0)

                if len(Tcharge_values_list) > 0:
                    self.TCC = self.dt2 * max(Tcharge_values_list)


            elif self.TCC_MODE == '1':
                self.TCC = 0
                for value in self.dict_Tcharge_by_sensor_id.values():

                    if (value > 0 and value < self.TMS_DL):
                        self.TCC += value
                        Nsyc += 1

                if Nsyc:
                    self.TCC = self.dt2 * self.TCC / Nsyc

            #             Mode 2: (Median(TCharge(1), TCharge(2), TCharge(3)))
            # If  0<TCharge(n)<( TMS_DL), Add TCharge(n) to a buffer
            # TCC = dt2*(median of the buffer)

            if self.TCC_MODE == '2':
                for value in self.dict_Tcharge_by_sensor_id.values():

                    if (value > 0 and value < self.TMS_DL):
                        Tcharge_values_list.append(int(value))

                if len(Tcharge_values_list) > 0:
                    self.TCC = self.dt2 * median(Tcharge_values_list)
                else:
                    self.TCC = 0




            elif self.TCC_MODE == '3':
                for value in self.dict_Tcharge_by_sensor_id.values():

                    if (value > 0 and value < self.TMS_DL):
                        Tcharge_values_list.append(int(value))
                    else:
                        Tcharge_values_list.append(0)

                if len(Tcharge_values_list) > 0:
                    value1 = max(Tcharge_values_list)

                    Tcharge_values_list.remove(value1)
                    if len(Tcharge_values_list) > 0:
                        value2 = max(Tcharge_values_list)
                        self.TCC = self.dt2 * (value1 + value2) / 2

                    else:
                        self.TCC = self.dt2 * value1
            if ATsycle > 0:
                self.CFT = self.dt2 * ATsycle - self.TCC;

            ts = {"ts": int(round(time.time() * 1000))}

            # if start_new_data:
            data = []

            new_obj_to_send = {"ts": ts["ts"], "values": {}}

            # Change - Start
            attr_to_send = calculate_info("CFT", self.CFT)
            #print(value_storage)
            #print(attr_to_send)
            self.user.send_attributes("PLC", attr_to_send)
            
            attr_to_send = calculate_info("TCC", self.TCC)
            #print(attr_to_send)
            self.user.send_attributes("PLC", attr_to_send)
            

            # new_obj_to_send["values"]["CFT"] = self.CFT
            new_obj_to_send["values"]["CFT"] = add_color_digit(self.CFT, "CFT")
            # new_obj_to_send["values"]["TCC"] = self.TCC
            new_obj_to_send["values"]["TCC"] = add_color_digit(self.TCC, "TCC")
            # Change - End

            data.append(new_obj_to_send)

            cftToSend = int(self.CFT * pow(2, 9))
            tccToSend = int(self.TCC * pow(2, 9))
            try:
                try:
                    if not self.plc_client == None:
                        result = self.plc_client.write_registers(1, [tccToSend], unit=0X01)
                        print("  TCC data sent to PLC :  " + str(tccToSend))
                        result = self.plc_client.write_registers(6, [cftToSend], unit=0X01)
                        print("  CFT data sent to PLC :  " + str(cftToSend))
                        result = self.plc_client.write_registers(9, [1], unit=0X01)
                        self.sendIsAlive()


                except Exception as e:
                    print("error sending data to PLC :  " + str(e))

                self.user.send_telemetry("PLC", data, False, None, None)

            except Exception as e:
                print("error sending data to Things Board :  " + str(e))
                # self.generalLogger.error("error sending data serv " + str(e))

            self.dict_Tcycle_A_2_by_sensor_id = {}
            self.dict_Tcharge_by_sensor_id = {}
            # self.timer = threading.Timer(min(5,int(self.TMS)), self.timerFunction)
            self.init_timer()

    def __new__(cls) -> __CalculatedParams:  # __new__ always a classmethod

        if not PlcCalculatedParams.instance:
            PlcCalculatedParams.instance = PlcCalculatedParams.__CalculatedParams()
            PlcCalculatedParams.instance.init_timer()
        return PlcCalculatedParams.instance


# Change - Start
attr_to_send = {}
saved_config = {}
value_storage = {"FWI": {"data": [], "counter": [0,0,0], "last_value_shift": 0},
                 "TCC": {"data": [], "counter": [0,0,0], "last_value_shift": 0},
                 "PSD": {"data": [], "counter": [0,0,0], "last_value_shift": 0},
                 "TBS": {"data": [], "counter": [0,0,0], "last_value_shift": 0},
                 "ABH": {"data": [], "counter": [0,0,0], "last_value_shift": 0},
                 "TBL": {"data": [], "counter": [0,0,0], "last_value_shift": 0},
                 "CFT": {"data": [], "counter": [0,0,0], "last_value_shift": 0},
                 "JCT": {"data": [], "counter": [0,0,0], "last_value_shift": 0}}



def calculate_info(param_name, value):
    attibutes = {}
    # Get configuration values
    global saved_config
    with open('config.txt', 'r') as infile:
        saved_config = json.load(infile)

    # Clean counters in case of new shift
    value_shift = determine_shift()
    if value_shift != value_storage[param_name]["last_value_shift"]:
        value_storage[param_name]["counter"] = [0, 0, 0]
        value_storage[param_name]["last_value_shift"] = value_shift

    # Add last value to storage list
    if len(value_storage[param_name]["data"]) == int(saved_config["N"]):
        value_storage[param_name]["data"].pop(0)
    elif len(value_storage[param_name]["data"]) > int(saved_config["N"]):
        slice_index = 1 - int(saved_config["N"])
        value_storage[param_name]["data"] = value_storage[param_name]["data"][slice_index:]
    value_storage[param_name]["data"].append(value)

    #print(value_storage[param_name]["data"])
    # Calculate Average and add Color digit (1=green, 2=yellow, 3=red)
    average = sum(value_storage[param_name]["data"]) / len(value_storage[param_name]["data"])
    #print(average)
    # Count values in pools of low/mid/high and calculate percentage
    if value < float(saved_config[param_name][0]):
        value_storage[param_name]["counter"][0] += 1
    elif value > float(saved_config[param_name][3]):
        value_storage[param_name]["counter"][2] += 1
    else:
        value_storage[param_name]["counter"][1] += 1

    counter_total = sum(value_storage[param_name]["counter"])
    percent_low = value_storage[param_name]["counter"][0] / counter_total * 100
    percent_high = value_storage[param_name]["counter"][2] / counter_total * 100
    percent_mid = 100 - percent_low - percent_high

    attibutes[param_name + "_AVG"] = add_color_digit(average, param_name)
    attibutes[param_name + "_COUNTER_LOW"] = value_storage[param_name]["counter"][0]
    attibutes[param_name + "_COUNTER_MID"] = value_storage[param_name]["counter"][1]
    attibutes[param_name + "_COUNTER_HIGH"] = value_storage[param_name]["counter"][2]
    attibutes[param_name + "_PRC_LOW"] = "{:.2f}%".format(percent_low)
    attibutes[param_name + "_PRC_MID"] = "{:.2f}%".format(percent_mid)
    attibutes[param_name + "_PRC_HIGH"] = "{:.2f}%".format(percent_high)

    return attibutes


def determine_shift():
    # Check if current time is during which shift
    # Taking in account that end of shift may be after midnight
    current_time = datetime.datetime.now().time()
    start_first_shift = datetime.datetime.strptime(saved_config["FIRST_SHIFT"][0], "%H:%M").time()
    end_first_shift = datetime.datetime.strptime(saved_config["FIRST_SHIFT"][1], "%H:%M").time()
    start_second_shift = datetime.datetime.strptime(saved_config["SECOND_SHIFT"][0], "%H:%M").time()
    end_second_shift = datetime.datetime.strptime(saved_config["SECOND_SHIFT"][1], "%H:%M").time()
    shift = 0
    
    if start_first_shift < end_first_shift:
        if start_first_shift > current_time < end_first_shift:
            shift = 1
    elif start_first_shift > end_first_shift:
        if start_first_shift > current_time or current_time < end_first_shift:
            shift = 1

    if start_second_shift < end_second_shift:
        if start_second_shift > current_time < end_second_shift:
            shift = 2
    elif start_second_shift > end_second_shift:
        if start_second_shift > current_time or current_time < end_second_shift:
            shift = 2
    return shift


def add_color_digit(value, param_name):
    # Add Color digit (1=green, 2=yellow, 3=red)
    if float(saved_config[param_name][1]) < value < float(saved_config[param_name][2]):
        return_value = "{:.3f}1".format(value)
    elif value < float(saved_config[param_name][0]) or value > float(saved_config[param_name][3]):
        return_value = "{:.3f}3".format(value)
    else:
        return_value = "{:.3f}2".format(value)
    return return_value

# Change - End
