from enum import Enum

'''
An enum class that represent option for the status of the spoofer object.
'''


class SpooferStatus(Enum):
    OFF = 0
    SCANNING = 1
    SPOOFING = 2
    RUNNING = 3
