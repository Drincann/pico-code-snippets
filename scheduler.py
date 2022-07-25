import time


class IOBase:
  def __init__(self) -> None:
    self.dataQueue: list = []

  def poll(self, timeoutms: int) -> None:
    time.sleep(timeoutms / 1000)


class Poll:
  def __init__(self) -> None:
    self.__ioTasks: list[IOBase] = []

  def polling(self, timeout: int = -1) -> dict[IOBase, list]:
    if len(self.__ioTasks) == 0:
      return {}
    start = time.ticks_ms()
    resultMap = {ioTask: [] for ioTask in self.__ioTasks}
    while True:
      if timeout > 0 and time.ticks_ms() - start > timeout:
        break
      hasEvent = False
      for ioTask in self.__ioTasks:
        ioTask.poll(10)
        if len(ioTask.dataQueue) > 0:
          hasEvent = True
          resultMap[ioTask].extend(ioTask.dataQueue)
          ioTask.dataQueue = []
      if not hasEvent:
        break
    return resultMap

  def register(self, ioTask: IOBase) -> None:
    self.__ioTasks.append(ioTask)

  def unregister(self, ioTask: IOBase) -> None:
    self.__ioTasks.remove(ioTask)

  def unregisterAll(self) -> None:
    self.__ioTasks = []

  def __len__(self) -> int:
    return len(self.__ioTasks)


class Timer:
  timerQueue: list = []

  def __init__(self, timeout: int, cbk) -> None:
    self.timeout = timeout
    self.end = time.ticks_ms() + self.timeout
    self.cbk = cbk

  def isTimeout(self) -> bool:
    return time.ticks_ms() - self.end > 0

  @ staticmethod
  def setTimeout(timeout: int, cbk) -> None:
    Timer.timerQueue.append(Timer(timeout, cbk))
    sorted(Timer.timerQueue, key=lambda timer: timer.end)

  @staticmethod
  def peek():
    if len(Timer.timerQueue) > 0:
      return Timer.timerQueue[0]
    return None


class EventLoop:
  def __init__(self) -> None:
    self.__poll = Poll()
    self.__ioTask2CbkMap = {}

  def run(self) -> None:
    while True:
      if len(Timer.timerQueue) == 0 and len(self.__poll) == 0:
        print('loop exit ')
        break
      while (timer := Timer.peek()) is not None and timer.isTimeout():
        Timer.timerQueue.pop(0)
        if callable(timer.cbk):
          timer.cbk()
      recentTimer = Timer.peek()
      timeout = recentTimer.end - time.ticks_ms() if recentTimer is not None else -1
      events = self.__poll.polling(timeout)
      for ioTask, data in events.items():
        cbk = self.__ioTask2CbkMap[ioTask]
        if callable(cbk):
          cbk(data)

  def register(self, ioTask: IOBase, cbk) -> None:
    self.__poll.register(ioTask)
    self.__ioTask2CbkMap[ioTask] = cbk

  def unregister(self, ioTask: IOBase) -> None:
    self.__poll.unregister(ioTask)

  def unregisterAll(self) -> None:
    self.__poll.unregisterAll()


loop = EventLoop()
