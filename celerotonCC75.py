import serial
import struct
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
        # dictionary for the variables, not all values included
        self.varDict = {"reference speed": 0,   # rpm
                        "actual speed": 1,      # rpm
                        "temperature": 4        # degree C
                        }
        # dict for the variable types
        # Int16 = 1, UInt16 = 2, Int32 = 3, UInt32 = 4, FLOAT = 5
        self.varTypeDict = {"reference speed": 3,
                            "actual speed": 3,
                            "temperature": 1
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
        """Get the current status.

        The function demands the current status of the controller.
        If there is a problem, the funtion tries to use method ackError
        to clear them.
        """
        statusByte = b'\x02\x00\xFE'
        self.write(statusByte)
        answer = self.read(16)
        try:
            statusInt = struct.unpack('<BBBBB', answer)
        except struct.error:
            statusInt = struct.unpack('<BBHHB', answer)
        statusString = self.statusDict[statusInt[2]]
        if 0 == statusInt[2]:
            print("Status is:", statusString)
            return
        elif (int('0008', 16) == statusInt[2] or
              int('0010', 16) == statusInt[2] or
              int('0020', 16) == statusInt[2]):
            self.ackError(answer, statusString)
        elif (int('0040', 16) == statusInt[2] or
              int('0080', 16) == statusInt[2]):
            print(statusString)
        else:
            raise ValueError('Unknown status code.')
        return

    def readValue(self, varName):
        """Read a selected value.

        The function reads the value of varName. Currently implemented:
        * "reference speed" in rpm
        * "actual speed" in rpm
        * "temperature" in Celsius

        :param varName: Desired value
        :type varName: str
        :returns varValue: Actual value
        :rtype varValue: int

        .. todo:: Complete all values
        """
        varFlag = self.varDict[varName]
        checkInt = self.checksum((3, 4, varFlag))
        readCommand = struct.pack('<BBBB', 3, 4, varFlag, checkInt)
        self.write(readCommand)
        answer = self.read(16)
        varType = answer[2]
        if (7 != answer[0]) or (4 != answer[1]):
            raise RuntimeError("Cannot interpret answer.")
        # Get the value according to its variable type
        if 1 == varType:
            answerInt = struct.unpack('<BBBhB', answer)
        elif 2 == varType:
            answerInt = struct.unpack('<BBBHB', answer)
        elif 3 == varType:
            answerInt = struct.unpack('<BBBiB', answer)
        elif 4 == varType:
            answerInt = struct.unpack('<BBBIB', answer)
        elif 5 == varType:
            answerInt = struct.unpack('<BBBfB', answer)
        else:
            raise ValueError("Cannot interpret answer.")
        varValue = answerInt[3]
        return varValue

    def writeValue(self, varName, varValue):
        """Write a selected value.

        The function writes the varValue of varName. Currently implemented:
        * "reference speed" in rpm
        * "actual speed" in rpm
        * "temperature" in Celsius

        :param varName: Desired value
        :type varName: str
        :param varValue: Actual value
        :type varValue: int

        .. todo:: Complete all values
        """
        varFlag = self.varDict[varName]
        varType = self.varTypeDict[varName]
        writeInt = (8, 5, varFlag, varType, varValue)
        if 1 == varType:
            writeCom = struct.pack('<BBBBh', *writeInt)
        elif 2 == varType:
            writeCom = struct.pack('<BBBBH', *writeInt)
        elif 3 == varType:
            writeCom = struct.pack('<BBBBi', *writeInt)
        elif 4 == varType:
            writeCom = struct.pack('<BBBBI', *writeInt)
        elif 5 == varType:
            writeCom = struct.pack('<BBBBf', *writeInt)
        else:
            raise ValueError("Cannot interpret answer.")
        checkInt = self.checksum(writeCom)
        writeCom += struct.pack('<B', checkInt)
        self.write(writeCom)
        answer = self.read(16)
        varType = answer[2]
        if (2 != answer[0])or(5 != answer[1])or(int('f9', 16) != answer[2]):
                raise RuntimeError("Cannot interpret answer.")
        return

    def errCheck(self, answer):
        """Takes the answer of the controller and raises error.

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

    def ackError(self, statusCode, statusStr):
        """Acknowledge an error

        The function takes the answered statusCode of the controller and the
        already found statusStr. The user is asked to acknowledge the error
        and, if answered with yes, the error is aknowledged.

        :param statusCode: Complete answer of the controller
        :type statusCode: bytes
        :param statusStr: String of the status (for user)
        :type statusStr: str
        """
        understand = False
        print('Status:', statusStr, '\n')
        while not understand:
            choice = input('Do you want to acknowledge the error?[y/N]: ')
            if choice == 'y' or choice == 'Y':
                understand = True
                statusInt = struct.unpack('<BBBBB', statusCode)
                checksum = self.checksum((4, 1,
                                          statusInt[2], statusInt[2]))
                # Create the command Byte
                ackInt = (4, 1, statusInt[2])
                ackBytes = struct.pack('<BBB', *ackInt)
                ackBytes = (ackBytes + struct.pack('>B', statusInt[2]) +
                            bytes([checksum]))
                self.write(ackBytes)
                answer = self.read(16)
                if b'\x02\x01\xfd' != answer:
                    raise RuntimeError('Cannot acknowledge error.')
                return
            elif 'n' == choice or 'N' == choice or '' == choice:
                understand = True
                raise RuntimeError("Error has not been acknowledged.")
            else:
                print("Cannot understand your input. Please repeat.")

    def reset(self):
        """Resets the controller.

        Because of invalid commands the controller can remain in a
        faulty state. The function sends 17  zero bits to the controller to
        clear the command status.
        """
        resetByte = (00000000000000000).to_bytes(17, byteorder='big')
        self.write(resetByte)
        answer = self.read()
        if (b'') is not answer:
            raise RuntimeError("Cannot reset controller.")
        return

    def checksum(self, command):
        """Computes the checksum

        For a given command, which is intended to be sent to the controller,
        the function computes the checksum

        :param command: Command for the controller
        :type command: tuple/list of int, bytes
        :returns checksum: String of the status (for user)
        :rtype checksum: int
        """
        if int == type(command):
            commandSum = sum(command)
            checksum = (~commandSum + 1) & 0xFF
        elif bytes == type(command):
            commandSum = sum(list(command))
            checksum = (~commandSum + 1) & 0xFF
        else:
            raise TypeError('Command must be int or bytes.')
        return checksum

    def monitor(self, valuename, threshold):
        """Monitor a variable and raises RuntimeError on threshold.

        The function 
        """
        pass


if __name__ == '__main__':
    logging.basicConfig(filename="DEBUG_celeroton.log",
                        level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s'
                        ' - %(message)s')
    ctCC75_400 = celerotonCC75('COM10')
    wantedVar = "reference speed"
    wantedValue = 600
    ctCC75_400.writeValue(wantedVar, wantedValue)
#     ctCC75_400.start()
#     time.sleep(3)
#     ctCC75_400.stop()
#     ctCC75_400.close()
