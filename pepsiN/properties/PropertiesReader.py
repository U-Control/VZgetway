from jproperties import Properties
#  
# configs = Properties()
# with open('../app-config.properties', 'rb') as config_file:
#     configs.load(config_file)
#     
#     
# print(configs.get("GATEWAY_NAME").data)  


class ConfParams: 
    class __ConfParams:
        configs=None
        def __init__(self):
            self.configs = Properties()
            with open('app-config.properties', 'rb') as config_file:
                self.configs.load(config_file)
           
        def getParam(self, name):
            return self.configs.get(name).data
            
            
    instance = None
    def __init__(self):
        if not ConfParams.instance:
            ConfParams.instance = ConfParams.__ConfParams()
        
    def getParam(self, name):
        return self.instance.getParam(name)