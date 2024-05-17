import subprocess
import re
import json




def getIP(interface):
    try:
        scan_result = \
            subprocess.Popen("ifconfig | grep " + interface + " -A 1", stdout=subprocess.PIPE, shell=True).communicate()[0]
        # Processing STDOUT into a dictionary that later will be converted to a json file later
        rInetAddr = r"inet addr:\s*([\d.]+)"
        mtIp = re.search(rInetAddr, scan_result)
        if mtIp and len(mtIp.groups()) == 1:
            return str(mtIp.group(1))
    except:
        return None


def getMac(interface):
    try:
        mac = subprocess.Popen(" cat /sys/class/net/" + interface + "/address", 
                               stdout=subprocess.PIPE, shell=True).communicate()[0].rstrip()
        if not mac:
            return "Not found"
        return mac.upper()
    except:
        return "Error"


def getWifiAp():
    try:
        ap = subprocess.Popen("iwgetid -r", 
                              stdout=subprocess.PIPE, shell=True).communicate()[0].rstrip()
        if not ap:
            return "Not connected"
        return ap
    except:
        return "Error"


def getHostname():
    try:
        hostname = subprocess.Popen("cat /etc/hostname", stdout=subprocess.PIPE, shell=True).communicate()[0].rstrip()
        if not hostname:
            return "Not connected"
        return hostname + ".local"
    except:
        return "Error"
