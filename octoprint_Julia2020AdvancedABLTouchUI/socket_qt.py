from PyQt4 import QtCore
from decorators import run_async
from config import ip
import random
import uuid
import json
import websocket


class QtWebsocket(QtCore.QThread):
    '''
    https://pypi.python.org/pypi/websocket-client
    https://wiki.python.org/moin/PyQt/Threading,_Signals_and_Slots
    '''

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
                                         on_close=self.on_close)

    def run(self):
        self.ws.run_forever()

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
                self.emit(QtCore.SIGNAL('CONNECTED'))



        if "plugin" in data:
            if data["plugin"]["plugin"] == 'Julia2018FilamentSensor':
                self.emit(QtCore.SIGNAL('FILAMENT_SENSOR_TRIGGERED'), data["plugin"]["data"])

            if data["plugin"]["plugin"] == 'JuliaFirmwareUpdater':
                self.emit(QtCore.SIGNAL('FIRMWARE_UPDATER'), data["plugin"]["data"])

            elif data["plugin"]["plugin"] == 'softwareupdate':
                if data["plugin"]["data"]["type"] == "updating":
                    self.emit(QtCore.SIGNAL('UPDATE_STARTED'), data["plugin"]["data"]["data"])
                elif data["plugin"]["data"]["type"] == "loglines":
                    self.emit(QtCore.SIGNAL('UPDATE_LOG'), data["plugin"]["data"]["data"]["loglines"])
                elif data["plugin"]["data"]["type"] == "restarting":
                    self.emit(QtCore.SIGNAL('UPDATE_LOG_RESULT'), data["plugin"]["data"]["data"]["results"])
                elif data["plugin"]["data"]["type"] == "update_failed":
                    self.emit(QtCore.SIGNAL('UPDATE_FAILED'), data["plugin"]["data"]["data"])

        if "current" in data:

            if data["current"]["messages"]:
                for item in data["current"]["messages"]:
                    if 'M206' in item: #response to M503, send current Z offset value
                        self.emit(QtCore.SIGNAL('Z_HOME_OFFSET'), item[item.index('Z') + 1:].split(' ', 1)[0])
                    # if 'Count' in item:  # gets the current Z value, uses it to set Z offset
                    #     self.emit(QtCore.SIGNAL('SET_Z_HOME_OFFSET'), item[item.index('Z') + 2:].split(' ', 1)[0],
                    #               False)

            if data["current"]["state"]["text"]:
                self.emit(QtCore.SIGNAL('STATUS'), data["current"]["state"]["text"])

            fileInfo = {"job": data["current"]["job"], "progress": data["current"]["progress"]}
            if fileInfo['job']['file']['name'] is not None:
                self.emit(QtCore.SIGNAL('PRINT_STATUS'), fileInfo)
            else:
                self.emit(QtCore.SIGNAL('PRINT_STATUS'), None)

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
                                    'bedActual': temp(data, "bed", "actual"),
                                    'bedTarget': temp(data, "bed", "target")}
                    self.emit(QtCore.SIGNAL('TEMPERATURES'), temperatures)
                except KeyError:
                    # temperatures = {'tool0Actual': data["current"]["temps"][0]["tool0"]["actual"],
                    #                 'tool0Target': data["current"]["temps"][0]["tool0"]["target"],
                    #                 'bedActual': data["current"]["temps"][0]["bed"]["actual"],
                    #                 'bedTarget': data["current"]["temps"][0]["bed"]["target"]}
                    pass
                # self.emit(QtCore.SIGNAL('TEMPERATURES'), temperatures)

    def on_open(self, ws):
        pass

    def on_close(self, ws):
        pass

    def on_error(self, ws, error):
        pass
