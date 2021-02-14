 
from pymodbus3.client.sync import ModbusTcpClient  
 
        # instead of this

       # 192.168.1.22:502
        #PLC Mod Bus Regs 40001-40100
        
        
 #40096-40100     monnth day hour .....  
#Reg 2 Bytes --> not 4 bytes     
 


plc_client = ModbusTcpClient('192.168.1.22')
# result =client.read_holding_registers(0,5,unit=0X01) 
# print (str(result))
try:
    for x in range(5,6):
        result = plc_client.write_registers( 9,[int(x)  ],unit=0X01) 
        result = plc_client.write_registers(40007,[int(x) ],unit=0X01) 
        result = plc_client.write_registers(40010,[int(1)],unit=0X01) 
 
    print (str(result))
except Exception as e:
    print("error sending data to plc " + str(e))
 

plc_client.close()