import errno
import json
import socket
import threading
from .sensorDataProcessing import *
from ThingBoardConection.client import ThingBoardUser


class TcpServer:
    instance = None

    class __TcpServer:

        get_status = b'\x12\x01\x01'

        user = ThingBoardUser()
        headersProcess = ProcessHeaders()

        function_process_data_to_view = None
        bind_ip = '0.0.0.0'
        bind_port = 9875
        dict_allSensor_by_id = {}

        list_sensors_send_coomend_read_raw_data = {}

        def recv_data(self, client_socket):

            try:

                self.headersProcess.headers = client_socket.recv(self.headersProcess.LANGTH_HEADERS)

                print("type data", self.headersProcess.type_data)
                self.headersProcess.data = client_socket.recv(self.headersProcess.len_data)

                # print("data", self.headersProcess.data)
            except socket.error as e:



                print("disconnect log ", e)

        def handle_client_connection(self, client_socket):

            processData = SensorDataProcess()

            time.sleep(10)

            client_socket.send(self.get_status)

            while True:

                self.recv_data(client_socket)
                ts = {"ts": SensorDataProcess.current_milli_time()}
                if self.headersProcess.id_sensor in self.list_sensors_send_coomend_read_raw_data and self.headersProcess.isRawData:
                    ts = self.list_sensors_send_coomend_read_raw_data[self.headersProcess.id_sensor]
                self.dict_allSensor_by_id[self.headersProcess.id_sensor] = client_socket
                if self.headersProcess.is_plc_data or self.headersProcess.isRawData or self.headersProcess.type_data == "end_of_pac":

                    id_socket, data = processData.process_data(ts)

                    if self.headersProcess.type_data == "end_of_pac" and id_socket in self.list_sensors_send_coomend_read_raw_data:
                        del self.list_sensors_send_coomend_read_raw_data[id_socket]

                    if id_socket not in self.list_sensors_send_coomend_read_raw_data:
                        try:
                            self.user.send_telemetry(id_socket, data)
                            processData.all_data = []
                        except Exception as e:
                            print("error sending data", e)
                else:
                    fer = self.function_process_data_to_view()

        def send_to_sensor(self, ids_sensor: list, data: str, read_sensor_raw_data_in_secods=None):
            if read_sensor_raw_data_in_secods:
                for i in ids_sensor:
                    if i not in self.list_sensors_send_coomend_read_raw_data:
                        self.list_sensors_send_coomend_read_raw_data[i] = read_sensor_raw_data_in_secods
            for i in ids_sensor:
                if i not in self.dict_allSensor_by_id:
                    return 'error id sensor ' + str(i)
                try:
                    self.dict_allSensor_by_id.get(i).send(data)
                except Exception as e:
                    print(e)
            return ''

        def run(self):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((self.bind_ip, self.bind_port))
            server.listen(8)  # max backlog of connections
            #   print('Listening on {}:{}'.format(self.bind_ip, self.bind_port))
            while True:
                print('Waiting for connection')
                client_sock, address = server.accept()
                print('Accepted connection from {}:{}'.format(address[0], address[1]))
                client_handler = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client_sock,))
                client_handler.start()

    def __new__(cls) -> __TcpServer:  # __new__ always a classmethod

        if not TcpServer.instance:
            TcpServer.instance = TcpServer.__TcpServer()
        return TcpServer.instance
