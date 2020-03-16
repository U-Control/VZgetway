import time

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

    read_raw_data_in_seconds = False

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

    def parse_data_from_sensor(self):

        if self.processHeaders.type_data.startswith("network"):
            self.write_data(self.processHeaders.type_data, self.processHeaders.data.decode())

        elif self.processHeaders.type_data == "algo_selected":
            self.algo_selected = int.from_bytes(self.processHeaders.data, byteorder="big")
            self.write_data(self.processHeaders.type_data,self.algoritem_options[self.algo_selected])

        elif self.processHeaders.type_data == "params" and self.params_logic[self.algo_selected]:
            for i in range(0, self.processHeaders.len_data, 2):
                value = int.from_bytes(self.processHeaders.data[i:i + 2], byteorder="big")
                self.write_data(self.params_logic[self.algo_selected][int(i / 2)], value)
        else:
            value = int.from_bytes(self.processHeaders.data, byteorder="big")
            self.write_data(self.processHeaders.type_data, value)

        # print(self.data_from_sensor)

        return self.data_from_sensor

    def convert_to_chars(self,data):
        self.data = ""

        for i in data:
            self.data += chr(i)

    def pars_cmd(self, data):
        data_send = bytes()
        self.id = data.get("id")
        del data["id"]
        if not self.id:
            return 'you must select sensor'
        message_error = ""
        for i in data:
            if i == "get_raw_data":
                self.read_raw_data_in_seconds = {"ts":int(round(time.time() * 1000))}
            if i == "rtc":
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
