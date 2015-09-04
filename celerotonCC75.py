import sys
import serial
import struct
import binascii
import io
import time
import logging
import struct


class celerotonCC75(serial.Serial):
    '''
    classdocs
    '''

    def __init__(self, serPort):
        '''
        Constructor
        '''
        super().__init__(serPort, baudrate=57600, stopbits=serial.STOPBITS_ONE,
                         bytesize=serial.EIGHTBITS, timeout=1, xonxoff=False,
                         rtscts=False, dsrdtr=False)
#         if str == type(serPort):
#             self.portstr = serPort
#         elif int == type(serPort):
#             self.port = serPort
#         else:
#             raise TypeError('serPort must be of type str or int.')
#         self.baudrate = 57600
#         self.stopbits = serial.STOPBITS_ONE
#         self.bytesize = serial.EIGHTBITS
#         self.timeout = 1                      # timeout in s
#         self.xonxoff = False
#         self.rtscts = False
#         self.dsrdtr = False
#         if not self.isOpen():
#             raise RuntimeError('Port cannot be opened.')
#         else:
#             logging.log(logging.DEBUG, "Port opened.")
        # Reset the controller to make sure it is not in faulty state
        self.reset()
        return

    def start(self):
        """Starts the motor.
        """
        startByte = b'\x02\x02\xFC'
        self.write(startByte)
        answer = self.read()
        if startByte is not answer:
            self.errCheck(answer)
        else:
            logging.log(logging.DEBUG, "Motor started.")
        return

    def stop(self):
        """Stops the motor.
        """
        stopByte = b'\x02\x03\xFB'
        self.write(stopByte)
        answer = self.read()
        if stopByte is not answer:
            self.errCheck(answer)
        else:
            logging.log(logging.DEBUG, "Motor stopped.")
        return

    def getStatus(self):
        # statusByte = b'\x02\x00\xFE'
        pass

    def readValue(self, valuename):
        pass

    def writeValue(self, valuename, valuenr):
        pass

    def errCheck(self, errCode):
        errInt = struct.unpack('>bbhhb', errCode)
        # Check for the error
        if int('0000', 16) == errInt[2]:
            print("Everthing OK.")
        elif int('4001', 16) == errInt[2]:
            raise RuntimeError('Unknown command.')
        elif int('4002', 16) == errInt[2]:
            raise RuntimeError('Wrong checksum.')
        elif int('4004', 16) == errInt[2]:
            raise RuntimeError('Invalid format.')
        elif int('4008', 16) == errInt[2]:
            raise RuntimeError('Read only.')
        elif int('4010', 16) == errInt[2]:
            raise RuntimeError('Type mismatch.')
        elif int('4020', 16) == errInt[2]:
            raise RuntimeError('Unknown variable.')
        else:
            raise RuntimeError('Cannot identify error.')
        return

    def ackError(self, errCode):
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

    def checksum(self, command):
        pass

    def hexInv(self, hexStr):
        val = int(hexStr, 8)
        nbits = 8  # Set the number of required bits
        invHexStr = hex((~val + (1 << nbits)) % (1 << nbits))
        return invHexStr

if __name__ == '__main__':
    logging.basicConfig(filename="DEBUG_celeroton.log",
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s'
                        ' - %(message)s')
    ctCC75_400 = celerotonCC75('COM10')
    ctCC75_400.start()
    ctCC75_400.stop()
