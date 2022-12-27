import json
import serial
import mongo
import time
from pymongo import MongoClient
from datetime import datetime
from pprint import pprint

import inc.mercury230 as mercury230
import inc.stm32 as stm32

from inc.utils import State
from inc.utils import ParametersMercury230
from inc.utils import ParametersStm32

# TODO: добавить вылеты из программы с нормальной обработкой
# TODO: заменить mongoBD на реляционную БД (SQLite, mySQL)

# чтение параметров из файла settings
with open('settings.json', 'r', encoding='utf-8') as settingsFile:
    allSettings = json.load(settingsFile)

settingsMercury230 = allSettings['mercury230']
# настройка COM-порта для Mercury230 и Stm32
serialMercury230 = serial.Serial(
    port=settingsMercury230['port'],
    baudrate=settingsMercury230['boudrate'],
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=settingsMercury230['timeout']
)

settingsStm32 = allSettings['stm32']
serialStm32 = serial.Serial(
    port=settingsStm32['port'],
    baudrate=settingsStm32['boudrate'],
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=settingsStm32['timeout']
)

# считываем общие параметры для стенда
settingsStand = allSettings['stend']
productSerialNum = settingsStand['productSerialNum']
brigadeNum = settingsStand['brigadeNum']
writeDatabase = bool(settingsStand['writeDatabase'])
writeConsole = bool(settingsStand['writeConsole'])

# настройка клиента БД
settingsMongoDB = allSettings['mongoDB']
client = MongoClient(settingsMongoDB['address'])
db = client[settingsMongoDB['database']] # получаем базу "ControlStand"
dbStend = db[settingsMongoDB['collection']] # получаем коллекцию "stend"

answer = mercury230.authorization(serialMercury230, settingsMercury230)
if (answer != State.OK):
    print('Error auth.')

# данные для отправки БД
package = {}

# Бесконечный цикл
print('start while')
while True:
    # mercury230
    P_SUM = mercury230.readParameter(serialMercury230, settingsMercury230, ParametersMercury230.P_SUM)
    package[ParametersMercury230.P_SUM.name] = P_SUM
    if P_SUM == 0:
        P_SUM = 1

    # stm32
    U_OUT = stm32.readParameter(serialStm32, settingsStm32, ParametersStm32.U_OUT)
    package[ParametersStm32.U_OUT.name] = U_OUT
    I_OUT = (stm32.readParameter(serialStm32, settingsStm32, ParametersStm32.I_OUT) / 1000) # mlAm -> Am
    package[ParametersStm32.I_OUT.name] = I_OUT
    efficiency = (U_OUT * I_OUT * 100) / P_SUM
    package['efficiency'] = efficiency # КПД

    # stand
    package['date'] = str(datetime.now().date())
    package['time'] = str(datetime.now().time())[:8]
    package['productSerialNum'] = productSerialNum
    package['brigadeNum'] = brigadeNum

    # отправка пакетов в БД
    if (writeDatabase):
        dbStend.insert_one(package)

    # печать в консоль
    if (writeConsole):
        pprint(package)

    # очистка пакета
    package = {}

    # TODO: проверка произовдится, когда плата подключается и оператор вводит команду
    time.sleep(1)