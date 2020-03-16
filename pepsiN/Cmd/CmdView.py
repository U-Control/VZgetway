import tkinter as tk
from tkinter import BooleanVar, Entry,IntVar

from TcpServer.sensorDataProcessing import algoParams


class CmdView:
    seconds_of_last_raw_data: Entry
    password: Entry
    SSId: Entry
    init_sensor: BooleanVar
    update_sensor_BIST: BooleanVar
    transmitting_row_data: BooleanVar
    pointer_leaser: BooleanVar
    handle_data_send = None

    entries = []

    algo_select = ""

    master = tk.Tk()

    algo_params = algoParams()

    algoritem_options = algo_params.algoritem_options



    fildes_by_algo = algo_params.params_logic

    check_box_text_and_value = {
        # "rtc": {
        #     "text": "update RTC",
        #     "value": tk.IntVar(),
        # },
        "pointer_leaser": {
            "text": "turn on/off pointer leaser",
            "value": tk.IntVar(),
        },
        "transmited_to_gatway": {
            "text": "enable/disable transmitting algoriten output to gateway",
            "value": tk.IntVar()
        },
        # "init_sensor":{
        #     "text": "init sensor",
        #     "value": tk.IntVar(),
        # },
        # "sensor_bist": {
        #     "text": "update sensor BIST",
        #     "value": tk.IntVar(),
        # } ,
        "transmited_row_data": {
            "text": "enable/disable transmitting row data to gateway",
            "value": tk.IntVar(),
        }
    }

    error_label = None

    updateRTC = None

    id_sensor = [0, 1, 2, 3, 4, 5, 6, 7, 8]

    params_input_element = []

    check_box_element = []

    prev_algo_select = ""

    port = ""

    ip_server = ""

    id_sensor_field:IntVar

    data = {}

    select_all = 0

    sensor_select = None

    list_bist = ["normal","saw","sinus"]

    option_element = None

    e1 = None

    def __init__(self, handle_data):
        self.handle_data_send = handle_data
        self.init_view()

    def add_bool_to_sender_data(self, filde, value):
        self.data[filde] = value.get()
        # print(self.data)

    def send_cmd(self):
        self.data["id"] = self.sensor_select.get() if not self.select_all.get() else 'all'
        if self.password.get():
            self.data["network_password"] = self.password.get()

        if self.SSId.get():
            self.data["network_name"] = self.SSId.get()

        if self.byte_to_sensor.get():
            self.data["byte_to_sensor"] = self.byte_to_sensor.get()

        if self.id_sensor_field.get():
            self.data["id_sensor"] = int(self.id_sensor_field.get())

        if self.sensor_bist.get():
            self.data["sensor_bist"] = self.list_bist.index(self.sensor_bist.get())

        if self.port.get():
            self.data["network_port"] = self.port.get()
            
        if self.seconds_of_last_raw_data.get():
            self.data["get_raw_data"] = int(self.seconds_of_last_raw_data.get())

        if self.ip_server.get():
            self.data["network_server_ip"] = self.ip_server.get()

        if self.algo_select.get():
            self.data["algo_selected"] = self.algoritem_options.index(self.algo_select.get())+2
            self.data["params"] = []
            for entryIndex in range(len(self.entries)):
                self.data["params"].append(self.entries[entryIndex].get())

        print(self.data)
        self.handle_data_send(self.data)

    def set_ids(self):
        self.option_element.pack_forget() if self.select_all.get() else self.option_element. \
            pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

    def show_error(self, message):
        self.error_label.config(text=message)

    def clear_params_list(self):
        self.entries = []
        for i in self.params_input_element:
            i.pack_forget()

        if self.data.get("params"):
            del self.data["params"]

    def set_params(self):

        self.clear_params_list()
        fildes = self.fildes_by_algo[self.algoritem_options.index(self.algo_select.get())]
        if not fildes:
            self.set_row_data_options()
            return

        self.option_element.pack_forget()
        for field in range(len(fildes)):
            row = tk.Frame(self.master)
            lab = tk.Label(row, width=15, text=fildes[field], anchor='w')
            ent = tk.Entry(row)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            self.params_input_element.append(row)
            self.params_input_element.append(lab)
            self.params_input_element.append(ent)
            self.entries.append(ent)

    def set_row_data_options(self):
        listi = ['distance only',"all data","velocity only"]
        row = tk.Frame(self.master)
        self.select_row_data_options = tk.StringVar(row)
        # row = tk.Frame(row)
        lab = tk.Label(row, width=15, text="choosing row data type", anchor='w')
        self.row_data_options_list = tk.OptionMenu(row, self.select_row_data_options, *listi)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        self.row_data_options_list.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)


    def get_status(self):
        idS = self.sensor_select.get() if not self.select_all.get() else 'all'
        # self.data["id"] = self.sensor_select.get() if not self.select_all.get() else 'all'
        self.clear_all()
        self.data["id"] = idS
        self.data["status"] = True
        self.handle_data_send(self.data)
        self.data = {}



    def set_check_box_view(self):

        for key, field in self.check_box_text_and_value.items():
            row = tk.Frame(self.master)
            # self.check_box_text_and_value[field]["value"] = tk.Variable()
            field["value"].set(0)
            c = tk.Checkbutton(row, text=field["text"], variable=field["value"])
            tk.Button(row, text='Apply', command=lambda field_text=key, value=field["value"]: self.add_bool_to_sender_data(field_text, value)).pack(side=tk.RIGHT, padx=3, pady=3)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            c.pack(side=tk.LEFT)

    def get_last_raw_data(self):
        idS = self.sensor_select.get() if not self.select_all.get() else 'all'
        # self.data["id"] = self.sensor_select.get() if not self.select_all.get() else 'all'
        self.clear_all()
        self.data["id"] = idS
        self.data["get_raw_data"] = True
        self.handle_data_send(self.data)
        self.data = {}

    def clear_all(self):
        self.data = {}
        for field in self.check_box_text_and_value:
            self.check_box_text_and_value[field]["value"].set(0)

        self.algo_select.set("")
        self.clear_params_list()
        self.SSId.delete(0, 'end')
        self.password.delete(0, 'end')
        self.port.delete(0, 'end')
        self.ip_server.delete(0, 'end')
        self.sensor_select.set("")
        self.select_all.set(0)
        self.id_sensor_field.set("")
        self.sensor_bist.set("")
        self.byte_to_sensor.delete(0, 'end')
        self.seconds_of_last_raw_data.delete(0, 'end')
        self.set_ids()

    def init_view(self):

        master = self.master
        row = tk.Frame(master)

        self.select_all = tk.IntVar()
        c = tk.Checkbutton(row, width=15, text="select all Sensors", variable=self.select_all, command=self.set_ids)
        row.pack(fill=tk.X, padx=5, pady=5)
        c.pack()

        self.sensor_select = tk.StringVar()
        row = tk.Frame(master)
        lab = tk.Label(row, width=15, text="select Sensor", anchor='w')
        self.option_element = tk.OptionMenu(row, self.sensor_select, *self.id_sensor)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        self.option_element.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        self.set_check_box_view()

        row = tk.Frame(self.master)
        lab = tk.Label(row, text="ESP WIFI Command  SSID-Password", anchor='w')
        self.SSId = tk.Entry(row)
        self.password = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        self.SSId.pack(side=tk.LEFT, expand=tk.YES)
        self.password.pack(side=tk.LEFT, expand=tk.YES)

        row = tk.Frame(self.master)
        lab = tk.Label(row, text="ESP WIFI Command  port-ip server", anchor='w')
        self.port = tk.Entry(row)
        self.ip_server = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        self.port.pack(side=tk.LEFT, expand=tk.YES)
        self.ip_server.pack(side=tk.LEFT, expand=tk.YES)

        row = tk.Frame(self.master)
        lab = tk.Label(row, text="Write bytes to vz sensor", anchor='w')
        self.byte_to_sensor = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        self.byte_to_sensor.pack(fill=tk.X, expand=tk.YES)

        row = tk.Frame(self.master)
        lab = tk.Label(row, text="Get the latest data in seconds", anchor='w')
        self.seconds_of_last_raw_data = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        self.seconds_of_last_raw_data.pack(fill=tk.X, expand=tk.YES)


        self.id_sensor_field = tk.StringVar(row)
        row = tk.Frame(master)
        lab = tk.Label(row, width=15,text="change id sensor", anchor='w')
        op = tk.OptionMenu(row, self.id_sensor_field, *self.id_sensor)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        op.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        self.sensor_bist = tk.StringVar(row)
        row = tk.Frame(master)
        lab = tk.Label(row, width=15,text="update sensor BIST", anchor='w')
        op = tk.OptionMenu(row, self.sensor_bist, *self.list_bist)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        op.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)



        self.algo_select = tk.StringVar()
        row = tk.Frame(master)
        lab = tk.Label(row, width=15, text="select algo", anchor='w')
        op = tk.OptionMenu(row, self.algo_select, *self.algoritem_options, command=lambda _: self.set_params())
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        op.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        self.error_label = tk.Label(master, fg="red")
        self.error_label.pack(padx=5, pady=5)

        tk.Button(master,
                  text='Send', command=self.send_cmd).pack(side=tk.RIGHT, padx=8, pady=8)
        tk.Button(master,
                  text='Clear', command=self.clear_all).pack(side=tk.RIGHT, padx=8, pady=8)
        tk.Button(master,
                  text='get status', command=self.get_status).pack(side=tk.RIGHT, padx=8, pady=8)
        # tk.Button(master,
        #           text='get last raw data', command=self.get_last_raw_data).pack(side=tk.RIGHT, padx=8, pady=8)

    @staticmethod
    def run():
        tk.mainloop()

# c = CmdView(15)
# c.run()
