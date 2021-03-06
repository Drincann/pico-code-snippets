import math
import time
import machine
_base = math.sin(math.pi/2)
_T = math.pi * 2


def play(pin: machine.Pin, speed: float = 1, granularity: int = 1000):
  """
  @param pin: machine.Pin  PIN to use
  @param speed: float      Speed of the wave
  @param granularity: int  Granularity of the wave
  """
  pwm = machine.PWM(pin)
  level = 0
  while True:
    level = (level + 1) % granularity
    currValue = int(
        (_base + math.sin(level * _T / granularity)) / 2 * 65534)
    pwm.duty_u16(currValue)
    time.sleep(1 / granularity / speed)
