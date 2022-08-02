import machine
import array
import rp2


class LED:
  def __init__(self, R: int, G: int, B: int, brightness: float):
    self.R = R
    self.G = G
    self.B = B
    self.brightness = brightness


class FrameContext:
  def __init__(self, ledController: "Controller"):
    self.ledController = ledController

  def __enter__(self):
    self.ledController.setFlush(False)
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.ledController.setFlush(True)
    return self


class Controller:

  BLACK = (0, 0, 0)
  RED = (255, 0, 0)
  YELLOW = (255, 150, 0)
  GREEN = (0, 255, 0)
  CYAN = (0, 255, 255)
  BLUE = (0, 0, 255)
  PURPLE = (180, 0, 255)
  WHITE = (255, 255, 255)
  single = None

  @staticmethod
  def getInstance(GPIOPin: machine.Pin = machine.Pin(21), ledCount: int = 64, brightness=0.1) -> "Controller":
    if Controller.single is None:
      Controller.single = Controller(
          GPIOPin=GPIOPin, ledCount=ledCount,
          shape=(8, 8), defaultBrightness=brightness
      )
    return Controller.single

  def __init__(self,
               GPIOPin: machine.Pin,
               ledCount: int,
               # (row, col)
               shape: tuple[int, int],
               defaultBrightness: float,
               ) -> None:
    @ rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
    def ws2812():
      T1 = 2
      T2 = 5
      T3 = 3
      wrap_target()
      label("bitloop")
      out(x, 1)               .side(0)[T3 - 1]
      jmp(not_x, "do_zero")   .side(1)[T1 - 1]
      jmp("bitloop")          .side(1)[T2 - 1]
      label("do_zero")
      nop()                   .side(0)[T2 - 1]
      wrap()
    self.__donotFlush = False
    self.__sm = rp2.StateMachine(
        0, ws2812, freq=8_000_000, sideset_base=GPIOPin
    )
    self.__sm.active(1)
    self.__brightness = defaultBrightness
    self.__leds = array.array("I", [0 for _ in range(ledCount)])
    self.__shape = shape
    self.__structuredLeds = [LED(0, 0, 0, 0) for _ in range(ledCount)]

  def setBrightness(self, brightness: float):
    self.__brightness = brightness

  def setColor1D(self, ledIndex: int, color: tuple, brightness=None) -> None:
    self.__structuredLeds[ledIndex].R = color[0]
    self.__structuredLeds[ledIndex].G = color[1]
    self.__structuredLeds[ledIndex].B = color[2]
    self.__structuredLeds[ledIndex].brightness = brightness if brightness is not None else self.__brightness
    self.__flush()

  def setColor2D(self, coord: tuple[int, int], color: tuple, brightness=None) -> None:
    rows = self.__shape[0]
    cols = self.__shape[1]
    ledIndex = coord[0] * cols + coord[1] \
        if coord[0] % 2 == 1 \
        else coord[0] * cols + rows - coord[1] - 1
    self.__flush()
    ledIndex = self.setColor1D(ledIndex, color, brightness)

  def clear(self, color: tuple = BLACK) -> None:
    for i in range(len(self.__leds)):
      self.__structuredLeds[i].R = color[0]
      self.__structuredLeds[i].G = color[1]
      self.__structuredLeds[i].B = color[2]
      self.__structuredLeds[i].brightness = self.__brightness
    self.__flush()

  def setFlush(self, flush: bool):
    self.__donotFlush = not flush
    if flush:
      self.__flush()

  def __flush(self):
    if self.__donotFlush:
      return
    for i in range(len(self.__structuredLeds)):
      led = self.__structuredLeds[i]
      self.__leds[i] = int(
          (int(led.G * led.brightness) << 16)
          + (int(led.R * led.brightness) << 8)
          + led.B * led.brightness
      )
    self.__sm.put(self.__leds, 8)

  def frame(self):
    return FrameContext(self)


con = Controller.getInstance()
