import serial
import utils
from utils import State
from enum import Enum

class Parameters(Enum):
    P_SUM = 0; P_1 = 1; P_2 = 2; P_3 = 3
    Q_SUM = 4; Q_1 = 5; Q_2 = 6; Q_3 = 7
    S_SUM = 8; S_1 = 9; S_2 = 10; S_3 = 11
    U_1 = 17; U_2 = 18; U_3 = 19
    I_1 = 33; I_2 = 34; I_3 = 35
    COS_SUM = 48; COS_1 = 49; COS_2 = 50; COS_3 = 51

def authorization(serial: serial.Serial, settings: dict):
    idMercury230 = settings['idMercury230']
    levelAccess = settings['levelAccess']
    password = settings['password']
    command = [idMercury230, 0x01, levelAccess]
    passwordList = list(map(int, str(password)))
    for pwd in passwordList:
        command.append(pwd)
    command = utils.addCRC16(command)
    answer = utils.sendCommand(serial, command, 4)
    if (utils.checkCRC16(list(answer)) == State.OK):
        # если CRC корректный, то смотрим, что получили от Mercury230
        # если авторизация прошла успешно, то должны получить answer[1] == 0
        if (answer[1] == 0):
            return State.OK
        else:
            return State.AUTH_ERR
    else:
        return State.CRC_ERR


def testConnection(serial: serial.Serial, settings: dict):
    idMercury230 = settings['idMercury230']
    command = [idMercury230, 0x00]
    command = utils.addCRC16(command)
    answer = utils.sendCommand(serial, command, 4)
    if (utils.checkCRC16(list(answer)) == State.OK):
        # если CRC корректный, то смотрим, что получили от Mercury230
        # если тест прошел успешно, то должны получить answer[1] == 0
        if (answer[1] == 0):
            return State.OK
        else:
            return State.ERR
    else:
        return State.CRC_ERR

def logout(serial: serial.Serial, settings: dict):
    idMercury230 = settings['idMercury230']
    command = [idMercury230, 0x02]
    command = utils.addCRC16(command)
    answer = utils.sendCommand(serial, command, 4)
    if (utils.checkCRC16(list(answer)) == State.OK):
        # если CRC корректный, то смотрим, что получили от Mercury230
        # если выход прошел успешно, то должны получить answer[1] == 0
        if (answer[1] == 0):
            return State.OK
        else:
            return State.ERR
    else:
        return State.CRC_ERR

def readParameter(serial: serial.Serial, settings: dict, parameter: Parameters):
    idMercury230 = settings['idMercury230']
    command = [idMercury230, 0x08, 0x11, parameter.value]
    command = utils.addCRC16(command)
    answer = utils.sendCommand(serial, command, 6)
    if (utils.checkCRC16(list(answer)) == State.OK):
        # если CRC корректный, то смотрим, что получили от Mercury230
        # расшифровываем результат, данные находятся в answer[1:3]
        hexNumber = ''.join(f'{i:02x}' for i in (answer[3], answer[2]))
        answer = int(hexNumber, 16)
        # в зависимости от параметра делим на 100 или на 1000
        if (parameter in (Parameters.COS_SUM, Parameters.COS_1, Parameters.COS_2,
        Parameters.COS_3, Parameters.I_1, Parameters.I_2, Parameters.I_3)):
            answer = answer / 1000.0000
        else:
            answer = answer / 100.0000
        return answer
    else:
        return State.CRC_ERR