 
from pymodbus3.client.sync import ModbusTcpClient  
 
        # instead of this

       # 192.168.1.22:502
        #PLC Mod Bus Regs 40001-40100
        
        
 #40096-40100     monnth day hour .....  
#Reg 2 Bytes --> not 4 bytes     
 


client = ModbusTcpClient('192.168.1.22')
result =client.read_holding_registers(0,5,unit=0X01) 
print (str(result))
result =client.write_registers(0,[300,305],unit=0X01) 
print (str(result))
 

client.close()