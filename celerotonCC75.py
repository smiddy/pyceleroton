import sys
import serial
import struct
import binascii
import io
import time
import logging


class celerotonCC75(serial.Serial):
    '''
    classdocs
    '''

    def __init__(self, serPort):
        '''
        Constructor
        '''
        self.port = serPort
        self.baudrate = 57600
        self.stopbits = serial.STOPBITS_ONE
        self.bytesize = serial.EIGHTBITS
        self.timeout = 1                      # timeout in s
        self.xonxoff = False
        self.rtscts = False
        self.dsrdtr = False
        pass

    def start(self):
        startByte = b'x\02x\02x\FC'
        self.write(startByte)
        answer = self.read()
        if startByte is not answer:
            self.errCheck(answer)
        else:
            logging.log(logging.DEBUG, "Motor started.")
        return

    def stop(self):
        pass

    def getStatus(self):
        statusByte = b'\x02\x00\xFE'
        pass

    def readValue(self, valuename):
        pass

    def writeValue(self, valuename, valuenr):
        pass

    def errCheck(self, errCode):
        pass

    def reset(self):
        resetByte = (00000000000000000).to_bytes(17, byteorder='big')
        self.write(resetByte)
        answer = self.read()
        if (b'\x00') is not answer:
            raise RuntimeError("Cannot reset controller.")
        return

    def monitor(self, valuename):
        pass

if __name__ == '__main__':
    logging.basicConfig(filename="DEBUG_celeroton.log",
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s'
                        ' - %(message)s')