from machine import UART, Pin
import time
from Scheduler import IOBase

ERROR_1 = b"ER+1\r\n"
ERROR_2 = b"ER+2\r\n"
ERROR_3 = b"ER+3\r\n"
ERROR_4 = b"ER+4\r\n"
ERROR_5 = b"ER+5\r\n"
ERROR_6 = b"ER+6\r\n"
ERROR_7 = b"ER+7\r\n"
ERROR_8 = b"ER+8\r\n"

BLE_MODE_PIN = Pin(15, Pin.IN, Pin.PULL_UP)

uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))


class IOBluetooth(IOBase):
  ErrorSet = {ERROR_1, ERROR_2, ERROR_3, ERROR_4, ERROR_5, ERROR_6, ERROR_7}

  def __init__(self) -> None:
    super().__init__()
    self.__connected = False

  def poll(self, timeoutms: int) -> None:

    start = time.ticks_ms()
    if self.__connected:
      # connected and ready to read
      while True:
        if uart.any() > 0:
          rxData = uart.read()
          if rxData in self.ErrorSet:
            self.__connected = False
            print('disconnected')
            break
          self.dataQueue.append(rxData)
        if time.ticks_ms() - start > timeoutms / 1000:
          break
      return
    else:
      # wait for connection
      while(BLE_MODE_PIN.value() == 0):
        time.sleep_ms(1)
        if time.ticks_ms() - start > timeoutms / 1000:
          break
      uart.read(1)
      while(True):
        rxData = uart.read(6)
        if rxData is not None:
          if(rxData in self.ErrorSet):
            self.__connected = False
          else:
            self.dataQueue.append('connected')
            self.__connected = True
            break
          if time.ticks_ms() - start > timeoutms / 1000:
            break
