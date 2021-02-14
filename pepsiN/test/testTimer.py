'''
Created on 23 Aug 2020

@author: USER
'''
import threading



def timerFunction( counter):
    print("timerFunction "+str( counter))
 
def initTimer(counter): 
    timer = threading.Timer(5.0, timerFunction , args =(counter,))
    timer.start()
    print("timer completed "+str( counter))  
 #   print('Listening on {}:{}'.format(self.bind_ip, self.bind_port))
counter=0   
initTimer(1)

# while True:
#     counter+=1
#     print('main loop '+str(counter))
#     timer_handler = threading.Thread(
#         target=initTimer,
#         args=(counter ))
#     timer_handler.start()  
#  

            
            

 
    