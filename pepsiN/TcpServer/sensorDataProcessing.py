import time
from enum import Enum, auto


class algoParams:
    algoritem_options = ["algo_2", "algo_3_4", "algo_5", "no_algo"]

    params_logic = [

        ["SPC", "Yv_th", "minStartN", "minStopN", "minResult", ],
        ["SPC", "th up", "th dn", "swichN", "MaxNBeforeSmPeak", "alpha", "FilterLength",
         "AveResultT"],
        ["SPC", "Yv_th", "FilterLength", "FilterLengthShort", "SwitchN", "alpha", "DToBelt",
         "Error2_th", "Error2_N", ],
        []
    ]

    paramsOut = [
        ["Result"],
        ["ResultT", "NoSmallPeak", "U1Ipoint", "U2Ipoint", "DIpoint", "AveU1Ipoint", "AveU2Ipoint", "AveDIpoint",
         "AveResultT", ],
        ["DeltaT", "ChBHight", "ST", "ErrorCode", "DToBelt"],
        []

    ]


class TypeData(Enum):
    velocity = 0
    distance = auto()
    algo_2 = auto()
    algo_3_4 = auto()
    algo_5 = auto()
    no_algo = auto()
    pointer_leaser = auto()
    transmited_to_gatway = auto()
    sensor_bist = auto()
    rtc = auto()
    algo_selected = auto()
    params = auto()
    network_name = auto()
    network_password = auto()
    network_port = auto()
    network_server_ip = auto()
    id_sensor = auto()
    transmited_row_data = auto()
    status = auto()
    bytes_from_sensor = auto()
    get_raw_data = auto()
    turn_on = auto()
    end_of_pac = 255


class ProcessHeaders:
    instance = None

    class __ProcessHeaders:
        len_data: int
        __headers = []

        ID_SENSOR_INDEX = 0

        LEN_DATA_INDEX_M = 1

        LEN_DATA_INDEX_L = 2

        TYPE_DATA = 3

        LANGTH_HEADERS = 4

        type_data = ""

        data: bytes = None

        @property
        def id_sensor(self):
            return self.headers[self.ID_SENSOR_INDEX]

        @property
        def headers(self):
            return self.__headers

        @property
        def is_plc_data(self):
            return TypeData[self.type_data].value < 5 and TypeData[self.type_data].value > 1

        @property
        def isRawData(self):
            return self.type_data == "velocity" or self.type_data == "distance"

        @headers.setter
        def headers(self, headers: bytes):
            # print("headers", headers)

            self.__headers = []

            for i in headers:
                self.__headers.append(i)

            bytes_row_data_length = headers[self.LEN_DATA_INDEX_M:self.LEN_DATA_INDEX_L + 1]

            self.len_data = int.from_bytes(bytes_row_data_length, byteorder="big")

            self.set_type_data()

        def set_type_data(self):
            try:
                self.type_data = TypeData(self.headers[self.TYPE_DATA]).name
            except Exception as e:
                print(str(self.headers) + '\n' + '-------------------------------------------------------------')
                print(str(self.data) + '\n' + '-------------------------------------------------------------')

        def set_headers_to_sensor(self, i, filde):
            return TypeData[i].value.to_bytes(1, byteorder='big') + (len(filde)).to_bytes(1, byteorder='big') + filde

    def __new__(cls) -> __ProcessHeaders:

        if not ProcessHeaders.instance:
            ProcessHeaders.instance = ProcessHeaders.__ProcessHeaders()
        return ProcessHeaders.instance


class SensorDataProcess:
    headersProcess = ProcessHeaders()

    all_data = []

    current_milli_time = lambda: int(round(time.time() * 1000))

    @property
    def id_sensor(self):
        return self.headersProcess.headers[self.headersProcess.ID_SENSOR_INDEX]

    def get_list_params(self):
        data_type_as_number = TypeData(self.headersProcess.headers[self.headersProcess.TYPE_DATA]).value
        return algoParams.paramsOut[data_type_as_number - 2]

    def process_data(self, start_timer=None) -> (str, dict):
        if not start_timer:
            ts = {"ts": SensorDataProcess.current_milli_time()}
        else:
            ts = start_timer

        # if start_new_data:
        #     self.all_data = []

        id_socket = self.id_sensor

        # increment = 1 if self.headersProcess.type_data == "plc_data" else 2

        list_params = self.get_list_params() if self.headersProcess.is_plc_data else None

        for i in range(0, self.headersProcess.len_data, 2):
            new_obj_to_send = {"ts": ts["ts"], "values": {}}

            try:
                type_data = list_params[int(i / 2)] if list_params else self.headersProcess.type_data

                new_obj_to_send["values"][type_data] = int.from_bytes(
                    self.headersProcess.data[i:i + 2], byteorder="big", signed=True)
                self.all_data.append(new_obj_to_send)
            except Exception as e:
                print("Error params" + str(self.headersProcess.headers))

            ts["ts"] += 1

        return id_socket, self.all_data
