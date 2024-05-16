from PyQt5 import QtCore
from decorators import run_async

class QtWebsocket(QtCore.QThread):
    '''
    https://pypi.python.org/pypi/websocket-client
    https://wiki.python.org/moin/PyQt/Threading,_Signals_and_Slots
    '''

    z_home_offset_signal = QtCore.pyqtSignal(str)
    temperatures_signal = QtCore.pyqtSignal(dict)
    status_signal = QtCore.pyqtSignal(str)
    print_status_signal = QtCore.pyqtSignal('PyQt_PyObject')
    update_started_signal = QtCore.pyqtSignal(dict)
    update_log_signal = QtCore.pyqtSignal(dict)
    update_log_result_signal = QtCore.pyqtSignal(dict)
    update_failed_signal = QtCore.pyqtSignal(dict)
    connected_signal = QtCore.pyqtSignal()
    filament_sensor_triggered_signal = QtCore.pyqtSignal(str)
    firmware_updater_signal = QtCore.pyqtSignal(dict)
    set_z_tool_offset_signal = QtCore.pyqtSignal(str,bool)
    tool_offset_signal = QtCore.pyqtSignal(str)
    active_extruder_signal = QtCore.pyqtSignal(str)
    z_probe_offset_signal = QtCore.pyqtSignal(str)
    z_probing_failed_signal = QtCore.pyqtSignal()
    printer_error_signal = QtCore.pyqtSignal(str)

    def __init__(self):

        super(QtWebsocket, self).__init__()

        url = "ws://{}/sockjs/{:0>3d}/{}/websocket".format(
            ip,  # host + port + prefix, but no protocol
            random.randrange(0, stop=999),  # server_id
            uuid.uuid4()  # session_id
        )
        self.ws = websocket.WebSocketApp(url,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         on_open=self.on_open)

    def run(self):
        self.ws.run_forever()

    def send(self, data):
        payload = '["' + json.dumps(data).replace('"', '\\"') + '"]'
        self.ws.send(payload)

    def authenticate(self):
        # perform passive login to retrieve username and session key for API key
        url = 'http://' + ip + '/api/login'
        headers = {'content-type': 'application/json', 'X-Api-Key': apiKey}
        payload = {"passive": True}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()

        # prepare auth payload
        auth_message = {"auth": "{name}:{session}".format(**data)}

        # send it
        self.send(auth_message)

    def on_message(self, ws, message):
        message_type = message[0]
        if message_type == "h":
            # "heartbeat" message
            return
        elif message_type == "o":
            # "open" message
            return
        elif message_type == "c":
            # "close" message
            return

        message_body = message[1:]
        if not message_body:
            return
        data = json.loads(message_body)[0]

        if message_type == "m":
            data = [data, ]

        if message_type == "a":
            self.process(data)

    @run_async
    def process(self, data):

        if "event" in data:
            if data["event"]["type"] == "Connected":
                self.connected_signal.emit()
                print("connected")
        if "plugin" in data:
            # if data["plugin"]["plugin"] == 'Julia2018FilamentSensor':
            #      self.filament_sensor_triggered_signal.emit(data["plugin"]["data"])

            if data["plugin"]["plugin"] == 'JuliaFirmwareUpdater':
                self.firmware_updater_signal.emit(data["plugin"]["data"])

            elif data["plugin"]["plugin"] == 'softwareupdate':
                if data["plugin"]["data"]["type"] == "updating":
                    self.update_started_signal.emit(data["plugin"]["data"]["data"])
                elif data["plugin"]["data"]["type"] == "loglines":
                    self.update_log_signal.emit(data["plugin"]["data"]["data"]["loglines"])
                elif data["plugin"]["data"]["type"] == "restarting":
                    self.update_log_result_signal.emit(data["plugin"]["data"]["data"]["results"])
                elif data["plugin"]["data"]["type"] == "update_failed":
                    self.update_failed_signal.emit(data["plugin"]["data"]["data"])

        if "current" in data:
            if data["current"]["messages"]:
                for item in data["current"]["messages"]:
                    if 'Filament Runout or clogged' in item: # "Filament Runout on T0/T1"
                        self.filament_sensor_triggered_signal.emit(item[item.index('T') + 1:].split(' ', 1)[0])
                    if 'M206' in item: #response to M503, send current Z offset value
                        self.z_home_offset_signal.emit(item[item.index('Z') + 1:].split(' ', 1)[0])
                    # if 'Count' in item:  # gets the current Z value, uses it to set Z offset
                    #     self.emit(QtCore.SIGNAL('SET_Z_HOME_OFFSET'), item[item.index('Z') + 2:].split(' ', 1)[0],
                    #               False)
                    if 'Count' in item:  # can get thris throught the positionUpdate event
                        self.set_z_tool_offset_signal.emit(item[item.index('z') + 2:].split(',', 1)[0],
                                  False)
                    if 'M218' in item:
                        self.tool_offset_signal.emit(item[item.index('M218'):])
                    if 'Active Extruder' in item:  # can get thris throught the positionUpdate event
                        self.active_extruder_signal.emit(item[-1])
                    
                    if 'M851' in item:
                        self.z_probe_offset_signal.emit(item[item.index('Z') + 1:].split(' ', 1)[0])
                    if 'PROBING_FAILED' in item:
                        self.z_probing_failed_signal.emit()
                    
                    items_to_ignore = [
                        #"Error",
                        "!! Printer is not ready",
                        "!! Move out of range:"#,
                        # "ok",
                        # "B:",
                        # "N",
                        # "echo: "
                    ]
                    # if item.startswith('!!') or (item.startswith('Error') and not item.startswith('!! Printer is not ready')):
                    #     self.printer_error_signal.emit(item)
                    #     print(item)
                    if item.strip():
                        for ignore_item in items_to_ignore:
                           if ignore_item in item:
                               print("ignored ->" + ignore_item)
                               # Ignore this item
                               break
                        else:
                           if item.startswith('!!') or item.startswith('Error'):
                           # If none of the items to ignore were found in 'item'
                            self.printer_error_signal.emit(item)
                            print(item)
                    #items_to_ignore_pattern = re.compile(r'^(?!ok$|!! Printer is not ready$|!! Move out of range:$ ).*|^Error.*')
                    # items_to_ignore_pattern = re.compile(r'(^Error)|(^!! Printer is not ready$)|(^!! Move out of range: .*$)|(ok)|(echo: )')
                    # if not items_to_ignore_pattern.search(item):
                    #     self.printer_error_signal.emit(item)
                    #     print('Called ->'+ item + '<-')

                    #items_to_ignore = ['!! Printer is not ready', '!! Move out of range:']
                    #if item.startswith('!!') or (item.startswith('Error') and item not in items_to_ignore):
                    #    self.printer_error_signal.emit(item)
                    #if item.startswith('!!') or item.startswith('Error'):
                    #    self.printer_error_signal.emit(item)
            if data["current"]["state"]["text"]:
                self.status_signal.emit(data["current"]["state"]["text"])

            fileInfo = {"job": data["current"]["job"], "progress": data["current"]["progress"]}
            if fileInfo['job']['file']['name'] is not None:
                self.print_status_signal.emit(fileInfo)
            else:
                self.print_status_signal.emit(None)

            def temp(data, tool, temp):
                try:
                    if tool in data["current"]["temps"][0]:
                        return data["current"]["temps"][0][tool][temp]
                except:
                    pass
                return 0

            if data["current"]["temps"] and len(data["current"]["temps"]) > 0:
                try:
                    temperatures = {'tool0Actual': temp(data, "tool0", "actual"),
                                    'tool0Target': temp(data, "tool0", "target"),
                                    'tool1Actual': temp(data, "tool1", "actual"),
                                    'tool1Target': temp(data, "tool1", "target"),
                                    'bedActual': temp(data, "bed", "actual"),
                                    'bedTarget': temp(data, "bed", "target")}
                    self.temperatures_signal.emit(temperatures)
                except KeyError:
                    # temperatures = {'tool0Actual': 0,
                    #                 'tool0Target': 0,
                    #                 'tool1Actual': 0,
                    #                 'tool1Target': 0,
                    #                 'bedActual': 0,
                    #                 'bedTarget': 0}
                    pass

    def on_open(self,ws):
        self.authenticate()

    def on_close(self, ws):
        pass

    def on_error(self, ws, error):
        print(error)
        pass