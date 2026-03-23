from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusDeviceContext
from pymodbus.datastore import ModbusServerContext

import threading
import time

# ================================
# Criando memória Modbus
# ================================
store = ModbusDeviceContext(
    di=ModbusSequentialDataBlock(0, [0]*100),
    co=ModbusSequentialDataBlock(0, [0]*100),
    hr=ModbusSequentialDataBlock(0, [0]*100),
    ir=ModbusSequentialDataBlock(0, [0]*100)  # INPUT REGISTERS
)

context = ModbusServerContext(devices=store, single=True)

# ================================
# Atualização dinâmica
# ================================
def update_values():
    value = 0
    while True:
        store.setValues(4, 0, [value])  # 4 = Input Register
        print(f"Valor enviado para o CLP: {value}")
        value += 1
        time.sleep(1)

threading.Thread(target=update_values, daemon=True).start()

# ================================
# Start servidor
# ================================
print("Servidor Modbus TCP rodando...")

StartTcpServer(
    context,
    address=("192.168.1.11", 502)
)