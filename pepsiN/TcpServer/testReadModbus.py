from uModBus.serial import Serial 
from uModBus.tcp import TCP
from network import WLAN
import machine 
 
print("hello")

slave_addr=0x0A
starting_address=0x9C40
register_quantity=10
signed=True

register_value = modbus_obj.read_holding_registers(slave_addr, starting_address, register_quantity, signed)
print('Holding register value: ' + ' '.join('{:d}'.format(x) for x in register_value))