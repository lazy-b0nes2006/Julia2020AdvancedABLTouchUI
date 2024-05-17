from PyQt4 import QtCore
from collections import OrderedDict

ip = '0.0.0.0:5000'
apiKey = 'B508534ED20348F090B4D0AD637D3660'

file_name = ''
Development = True
    #Update


filaments = [
                ("PLA", 220),
                ("ABS", 240),
                ("PETG", 240),
                ("PVA", 230),
                ("TPU", 240),
                ("Nylon", 250),
                ("PolyCarbonate", 265),
                ("HIPS", 240),
                ("WoodFill", 220),
                ("CopperFill", 200),
                ("Breakaway", 240)
]

filaments = OrderedDict(filaments)

calibrationPosition = {'X1': 163, 'Y1': 20,
                       'X2': 32, 'Y2': 20,
                       'X3': 97, 'Y3': 193
                       }

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s