'''
Created on 17 Aug 2020

@author: USER
'''
data=None
command_file="C:\\Users\USER\Desktop\SW\Gateway Sensors\server\pepsi\VZC\example\commands.csv"        # Using readlines() 
file1 = open(command_file, 'r') 
Lines = file1.readlines() 
file1.close()
 
for line in Lines:
    write_command_length=None
   
