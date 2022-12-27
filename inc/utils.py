import serial
import crcmod
from enum import Enum

class State(Enum):
    OK = 0
    ERR = 1
    CRC_ERR = 2
    AUTH_ERR = 3

def sendCommand(serial: serial.Serial, command: bytearray, countBytesAnswer):
    serial.write(command)
    answer = serial.read(countBytesAnswer)
    return list(answer)

def addCRC16(command: list):
    hexCommand = bytes(command).hex()
    bytesCommand = bytes.fromhex(hexCommand)
    # подсчитываем crc16
    crc16 = crcmod.mkCrcFun(0x18005, initCrc=0xFFFF, rev=True,  xorOut=0x0000)
    crc_int=crc16(bytesCommand) 
    # создаем новый список с crc16 и переводим его в bytes
    crc_lo = (crc_int & 0x00FF)
    crc_hi = (crc_int & 0xFF00) >> 8
    command.append(crc_lo)
    command.append(crc_hi)
    return command

def checkCRC16(answer: list):
    sizeAnswer = len(answer)
    crc_hi = answer[sizeAnswer - 1] #последний элемент массива
    crc_lo = answer[sizeAnswer - 2] # предпоследний элемент массива
    del answer[sizeAnswer - 2: sizeAnswer] # удаляем CRC из списка
    # подстчитываем CRC
    answer = addCRC16(answer)
    # сравниваем CRC
    new_crc_hi = answer[sizeAnswer - 1]
    new_crc_lo = answer[sizeAnswer - 2]
    if (crc_hi != new_crc_hi) or (crc_lo != new_crc_lo):
        return State.CRC_ERR
    else:
        return State.OK