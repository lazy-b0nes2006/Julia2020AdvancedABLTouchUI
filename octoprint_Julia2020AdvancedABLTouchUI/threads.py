from PyQt4 import QtCore
from octoprintAPI import octoprintAPI
import subprocess
from config import ip, apiKey
import time
import os
from network_utils import getIP

class ThreadSanityCheck(QtCore.QThread):
    def __init__(self, logger, virtual=False):
        super(ThreadSanityCheck, self).__init__()
        self.MKSPort = None
        self.virtual = virtual
        self._logger = logger

    def run(self):
        global octopiclient
        shutdown_flag = False
        # get the first value of t1 (runtime check)
        uptime = 0
        # keep trying untill octoprint connects
        while (True):
            # Start an object instance of octopiAPI
            try:
                if (uptime > 30):
                    shutdown_flag = True
                    self.emit(QtCore.SIGNAL('STARTUP_ERROR'))
                    break
                octopiclient = octoprintAPI(ip, apiKey)
                result = subprocess.Popen("dmesg | grep 'ttyUSB'", stdout=subprocess.PIPE, shell=True).communicate()[0]
                result = result.split('\n')  # each ssid and pass from an item in a list ([ssid pass,ssid paas])
                result = [s.strip() for s in result]
                if not self.virtual:
                    result = subprocess.Popen("dmesg | grep 'ttyUSB'", stdout=subprocess.PIPE, shell=True).communicate()[0]
                    result = result.split('\n')  # each ssid and pass from an item in a list ([ssid pass,ssid paas])
                    result = [s.strip() for s in result]
                    for line in result:
                        if 'ch341-uart' in line:
                            self.MKSPort = line[line.index('ttyUSB'):line.index('ttyUSB') + 7]
                            print (self.MKSPort)
                        elif 'FTDI' in line:
                            self.MKSPort = line[line.index('ttyUSB'):line.index('ttyUSB') + 7]
                            print (self.MKSPort)

                if not self.MKSPort:
                    octopiclient.connectPrinter(port="VIRTUAL", baudrate=115200)
                else:
                    octopiclient.connectPrinter(port="/dev/" + self.MKSPort, baudrate=115200)
                break
            except Exception as e:
                time.sleep(1)
                uptime = uptime + 1
                # print "Not Connected!"
                print(e.message)
                self._logger.error("ThreadSanityCheck: " + str(e.message))
        if not shutdown_flag:
            self.emit(QtCore.SIGNAL('LOADED'))


class ThreadFileUpload(QtCore.QThread):
    def __init__(self, file, prnt=False):
        super(ThreadFileUpload, self).__init__()
        self.file = file
        self.prnt = prnt

    def run(self):

        try:
            exists = os.path.exists(self.file.replace(".gcode", ".png"))
        except:
            exists = False
        if exists:
            octopiclient.uploadImage(self.file.replace(".gcode", ".png"))

        if self.prnt:
            octopiclient.uploadGcode(file=self.file, select=True, prnt=True)
        else:
            octopiclient.uploadGcode(file=self.file, select=False, prnt=False)


class ThreadRestartNetworking(QtCore.QThread):
    WLAN = "wlan0"
    ETH = "eth0"

    def __init__(self, interface, signal):
        super(ThreadRestartNetworking, self).__init__()
        self.interface = interface
        self.signal = signal

    def run(self):
        self.restart_interface()
        attempt = 0
        while attempt < 3:
            if getIP(self.interface):
                self.emit(QtCore.SIGNAL(self.signal), getIP(self.interface))
                break
            else:
                attempt += 1
                time.sleep(1)
        if attempt >= 3:
            self.emit(QtCore.SIGNAL(self.signal), None)

    def restart_interface(self):
        '''
        restars wlan0 wireless interface to use new changes in wpa_supplicant.conf file
        :return:
        '''
        subprocess.call(["ifdown", "--force", self.interface], shell=False)
        subprocess.call(["ifup", "--force", self.interface], shell=False)
        time.sleep(5)
