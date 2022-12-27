import serial
import utils
from enum import Enum

class Parameters(Enum):
    U_OUT = 0x63; I_OUT = 0x64 
    I_PROTECT = 0x65; I_ACTIV = 0x66 
    UI_CORR = 0x67
    CONTROL_ERR = 0x68
    ERR_CORR = 0x69

def readParameter(serial: serial.Serial, settings: dict, parameter: Parameters):
    idStm32 = settings['idStm32']
    command = [idStm32, 0x03, 0x00, parameter.value, 0x00, 0x01]
    command = utils.addCRC16(command)
    answer = utils.sendCommand(serial, command, 7)
    hexNumber = ''.join(f'{i:02x}' for i in (answer[3], answer[4]))
    answer = int(hexNumber, 16)
    return answer

# TODO: что и куда будем отправлять?
def writeParameter(serial: serial.Serial, settings: dict, parameter: Parameters, hibyte: int, lobyte: int):
    # проверка передаваемого параметра для записи
    idStm32 = settings['idStm32']
    command = [idStm32, 0x04, 0x00, parameter.value, 0x00, 0x01, hibyte, lobyte]
    command = utils.addCRC16(command)
    answer = utils.sendCommand(serial, command, 7)
    hexNumber = ''.join(f'{i:02x}' for i in (answer[3], answer[4]))
    answer = int(hexNumber, 16)
    return answer