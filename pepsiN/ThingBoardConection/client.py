import requests
import json
import logging
from logging.handlers import RotatingFileHandler
from properties.PropertiesReader import ConfParams
#from ThingBoardConection.BinaryFileBuffer import   RotatingBinaryFileBuffer
#from Tools.scripts.make_ctype import values
import time
import os
from TcpServer.clientTest import host, port

class ThingBoardUser:

    instance = None
   
    
    def __new__(cls):

        if not ThingBoardUser.instance:
            ThingBoardUser.instance = ThingBoardUser.__ThingBoardUser()
        return ThingBoardUser.instance

    class __ThingBoardUser:
        params=ConfParams() 
        telemetry_url = '/api/v1/{}/telemetry'
        attributes_url = '/api/v1/{}/attributes'
        port = params.getParam("TB_PORT")

        host = 'http://localhost'

        user = {
            "username": "tenant@thingsboard.org",
            "password": "tenant"
        }

        token = "Bearer "

        refreshToken = ""

        headers = {

        }
        logger_v = logging.getLogger('rawData_V_logger')
        handler = RotatingFileHandler('./Recorded_Raw_Data/rawData_V.log', maxBytes=20000000, backupCount=200)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        logger_v.addHandler(handler)
        logger_v.setLevel(logging.DEBUG)
        
        logger_d = logging.getLogger('rawData_D_logger')
        handler = RotatingFileHandler('./Recorded_Raw_Data/rawData_D.log', maxBytes=20000000, backupCount=200)
        
        handler.setFormatter(formatter)
        
        logger_d.addHandler(handler)
        logger_d.setLevel(logging.DEBUG)
      
        binLoggers={}
        
        
         
        
        @staticmethod
        def access_token(id_device):
            return str(id_device) + '_prex'

        def __init__(self):
            self.login()
            

        def set_headers(self, header_key, header_value):
            self.headers[header_key] = header_value

        def login(self, refresh=None):

            self.token = "Bearer "
            url = '/api/auth/login' if not refresh else '/api/auth/token'

            body = json.dumps(self.user) if not refresh else json.dumps({"refreshToken": self.refreshToken})

            re = self.post(url, body)
 #http://localhost:8080/deviceGroups/c19f6a00-e2a6-11ea-9233-194f88fa09ad
            if re.status_code == 200:
                re = json.loads(re.text)
                self.refreshToken = re.get("refreshToken")
                self.token += re.get("token")
                self.set_headers('X-Authorization', self.token)

        def get(self, path):

            re = requests.get(url=self.get_url(path), headers=self.headers)
            if re.status_code == 401 and json.loads(re.text).get("message") == "Token has expired":
                self.login(True)
                self.get(path)
            return re

        def post(self, path, body):
            return requests.post(url=self.get_url(path), data=body)

        def get_url(self, path):
            return self.host + ":" + self.port + path

        def get_bin_filename(self,basename):
        # append year and week number to basename ]_[year]_[month][day]_[h]_[m][s].bin
            return '{}_{}.bin'.format( \
                 basename, time.strftime('%Y_%m_%d_%H_%M_%S'))
            
             
        def send_attributes(self, id_device, data):
            try:
                jsonData = json.dumps(data)
                # print(jsonData)
                re = self.post(self.attributes_url.format(self.access_token(id_device)), jsonData)
                # print("url: ",re.status_code)
                # print("Sending attributes data succeeded: "+str(jsonData))

            except requests.exceptions.RequestException as e:
                print(e)
                return False
            
        
        def send_telemetry(self, id_device, data,isRawData,binData,rawDataType,send_keep_alive=False):
            #fi = ""
            #type_data = ""
            i=data[0] 
#             for i in data:
#                 for j in i["values"]:
#                     fi +=  str(id_device)+','+str(i["values"][j]) + ',\n'
#                     if not type_data:
#                         type_data = j
            # print(self.all_data)
                           
                
            if(isRawData):
                if(rawDataType=="velocity"):
                    self.logger_v.debug(i)
                else: 
                    self.logger_d.debug(i)
                
                
                id_deviceStr=str(id_device) 
              
                binLoggerSize=0
                binLogger=self.binLoggers.get(rawDataType+id_deviceStr)
              
                if(binLogger != None):
                    binLoggerSize=os.path.getsize(binLogger.name)
                
                 
                if( binLogger == None or  binLoggerSize >2000000):
                    # #RD[SN]_[year]_[month][day]_[h]_[m][s].bi
                    if(binLoggerSize >2000000):
                        binLogger.close()
                                                
                    binLogger=open(self.get_bin_filename('./Recorded_Raw_Data/RD_'+rawDataType+'_'+id_deviceStr), 'ba')
                    
                    #binLogger = RotatingBinaryFileBuff)r('./Recorded_Raw_Data/RD_'+rawDataType+'_'+id_deviceStr)
                    self.binLoggers[rawDataType+id_deviceStr]=binLogger
                    
                binLogger.write(binData) 
                binLogger.flush()
                if send_keep_alive:
                    data={"ts": int(round(time.time() * 1000)), "values": {"is_alive":True}}
                    jsonData=json.dumps(data)
                    re = self.post(self.telemetry_url.format(self.access_token(id_device)), jsonData)

                print(self.telemetry_url.format(self.access_token(id_device)))
                print("Sending telemetry data succeeded: "+str(jsonData))
                print(re)

            try:
                if(not isRawData):
                    # print("Wait for the data to be uploaded")
                    jsonData=json.dumps(i)
              #      jsonData= jsonData[3:len(jsonData)]
                  
                    re = self.post(self.telemetry_url.format(self.access_token(id_device)), jsonData)
                    #print("Sending data succeeded: "+str(jsonData))
            except requests.exceptions.RequestException as e:
                print(e)
                return False
               
                if(not isRawData):
                    if re.status_code != 200:
                        print("error sending data", re.reason)
                        return False
            # for i in data:
            #     i = json.dumps(i).encode()
            #     try:
            #         re = self.post(self.telemetry_url.format(self.access_token(id_device)), i)
            #     except requests.exceptions.RequestException as e:
            #         print(e)
            #         return False
            #     if re.status_code != 200:
            #         print("error sending data", re)
            #         return False
            # print("sending data complet")

        def __str__(self):
            return repr(self)
