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
        # Import the existing constructor
        super().__init__(serPort, baudrate=57600, stopbits=serial.STOPBITS_ONE,
                         bytesize=serial.EIGHTBITS, timeout=1, xonxoff=False,
                         rtscts=False, dsrdtr=False)
        self.reset()
        # dictionary for error messages
        self.errDict = {int('0000', 16): 'OK',
                        int('4001', 16): 'Unknown command',
                        int('4002', 16): 'Wrong checksum',
                        int('4004', 16): 'Invalid format',
                        int('4008', 16): 'Readonly',
                        int('4010', 16): 'Type mismatch',
                        int('4020', 16): 'Unknown variable',
                        }
        # dictionary for status messages
        self.statusDict = {int('0000', 16): 'OK',
                           int('0008', 16): 'Overtemperature',
                           int('0010', 16): 'Overvoltage',
                           int('0020', 16): 'Undervoltage',
                           int('0040', 16): 'Stall 1',
                           int('0080', 16): 'Stall 2',
                           int('0100', 16): 'Stall 3',
                           int('0200', 16): 'Overspeed',
                           int('4000', 16): 'Enable',
                           int('8000', 16): 'Motor overtemperature'
                           }
        return

    def start(self):
        """Starts the motor.
        """
        startByte = b'\x02\x02\xFC'
        self.write(startByte)
        answer = self.read(16)
        if startByte != answer:
            self.errCheck(answer)
        else:
            logging.log(logging.DEBUG, "Motor started.")
        return

    def stop(self):
        """Stops the motor.
        """
        stopByte = b'\x02\x03\xFB'
        self.write(stopByte)
        answer = self.read(16)
        if stopByte != answer:
            self.errCheck(answer)
        else:
            logging.log(logging.DEBUG, "Motor stopped.")
        return

    def getStatus(self):
        statusByte = b'\x02\x00\xFE'
        self.write(statusByte)
        answer = self.read(16)
        # Case for OK status
        if 5 == len(answer):
            statusInt = struct.unpack('<bbbbb', answer)
            statusString = self.statusDict[statusInt[2]]
            if 0 == statusInt[2]:
                print(statusString)
                return
            elif (int('0008', 16) == statusInt[2] or
                  int('0010', 16) == statusInt[2] or
                  int('0020', 16) == statusInt[2]):
                self.ackError(answer)
            elif (int('0040', 16) == statusInt[2] or
                  int('0080', 16) == statusInt[2]):
                print(statusString)
            else:
                raise ValueError('Unknown status code.')
        elif 7 == len(answer):
            statusInt = struct.unpack('<bbhhb', answer)
            statusString = self.statusDict[statusInt[2]]
            if (int('0200', 16) == statusInt[2]):
                self.ackError(answer)
            elif (int('0100', 16) == statusInt[2] or
                  int('4000', 16) == statusInt[2] or
                  int('8000', 16) == statusInt[2]):
                print(statusString)
            else:
                raise ValueError('Unknown status code.')
            print(statusString)
        else:
            raise ValueError('Unknown status code.')
        return

    def readValue(self, valuename):
        pass

    def writeValue(self, valuename, valuenr):
        pass

    def errCheck(self, answer):
        """Takes the answer of the controller and raises error

        :param answer: Answer of the controller
        :type answer: bytes
        """
        errInt = struct.unpack('<bbhhb', answer)
        try:
            errString = self.errDict[errInt[2]]
            raise RuntimeError(errString)
        except:
            raise ValueError('Unknown error code.')
        return

    def ackError(self, errCode):
        pass

    def reset(self):
        resetByte = (0000000000000000).to_bytes(16, byteorder='big')
        self.write(resetByte)
        answer = self.read()
        if (b'') is not answer:
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
    ctCC75_400.getStatus()
#     ctCC75_400.start()
#     time.sleep(3)
#     ctCC75_400.stop()
#     ctCC75_400.close()
