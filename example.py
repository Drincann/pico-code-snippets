from Scheduler import loop
from IOUtils import onBluetoothData
from SnackGame import SnakeGame
import time
from LEDController import con
countDown = [
    [[0,   0, 233, 132, 129, 231,   0,   0],
     [0,   0,  66, 170, 169,  61,   0,   0],
     [0, 212,  72,   0,   0,  80, 204,   0],
     [0, 178, 103,   0,   0, 106, 174,   0],
     [0, 176, 103,   0,   0, 105, 173,   0],
     [0, 207,  79,   0,   0,  88, 196,   0],
     [0,   0,  54, 207, 210,  50, 247,   0],
     [0,   0, 212,  95,  93, 208,   0,   0]],
    [[0,   0,   0, 187,  23, 187,   0,   0],
     [0,   0, 174,  81,  74, 187,   0,   0],
     [0,   0, 248,   0,  97, 187,   0,   0],
     [0,   0,   0,   0,  98, 187,   0,   0],
     [0,   0,   0,   0,  98, 187,   0,   0],
     [0,   0,   0,   0,  98, 187,   0,   0],
     [0,   0,   0,   0, 149, 209,   0,   0]],
    [[0, 229,  44, 183, 181,  41, 234,   0],
     [0, 213, 163,   0,   0,  73, 198,   0],
     [0,   0,   0,   0, 207,  41, 242,   0],
     [0,   0,   0, 198,  46, 202,   0,   0],
     [0,   0, 173,  53, 214,   0,   0,   0],
     [0, 211,  24, 163, 188, 188, 237,   0],
     [0, 178,  98,  98,  98,  98, 214,   0]],
    [[0,   0,  70, 145, 172,  49, 242,   0],
     [0, 248, 159,   0,   0,  62, 213,   0],
     [0,   0,   0, 212,  94,  86,   0,   0],
     [0,   0,   0, 227, 186,  55, 194,   0],
     [0, 246, 200,   0,   0, 149, 118,   0],
     [0, 242,  41, 214, 241,  71, 171,   0],
     [0,   0, 199,  83,  74, 150,   0,   0]]
]
countDown.reverse()


def setImg(img):
  with con.frame():
    for i in range(len(img)):
      for j in range(len(img[i])):
        con.setColor2D((i, j), con.GREEN, brightness=img[i][j] / 2000)


def gamestart():

  WALL = SnakeGame.WALL
  EMPTY = SnakeGame.EMPTY
  game = SnakeGame(map=[
      [WALL, WALL, WALL, WALL, WALL, WALL, WALL, WALL],
      [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
      [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
      [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
      [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
      [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
      [WALL, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, WALL],
      [WALL, WALL, WALL, WALL, WALL, WALL, WALL, WALL],
  ],
      snake=[(6, 4), (5, 4), (4, 4)],
      direction=SnakeGame.UP,
      speed=1.7,
  )

  def onData(data):
    while len(data) != 0:
      cmd = data.pop(0)
      if cmd == 'connected':
        print('connected')
        for numImg in countDown:
          setImg(numImg)
          time.sleep(0.5)
        game.begin(gameCallback)
        return
      if cmd.decode() in directionChangeMap:
        print(cmd)
        game.changeDirection(directionChangeMap[cmd.decode()])
      else:
        print(cmd)
  onBluetoothData(onData)

  def gameCallback(
      state: int,
      wallSet: set[tuple[int, int]],
      snake: list[tuple[int, int]],
      food: tuple[int, int],
  ):
    if state == SnakeGame.RUNNING:
      with con.frame():
        con.clear()
        for wall in wallSet:
          con.setColor2D(wall, con.RED)
        for snakeBody in snake:
          con.setColor2D(snakeBody, con.WHITE)
          con.setColor2D(food, con.GREEN)

    elif state == SnakeGame.GAMEOVER:
      # over
      with con.frame():
        for wall in wallSet:
          con.setColor2D(wall, con.RED)
        for snakeBody in snake:
          con.setColor2D(snakeBody, con.WHITE)
          con.setColor2D(food, con.GREEN)
      loop.unregisterAll()
      # time.sleep(1)
      for i in range(64):
        con.setColor1D(i, con.RED, brightness=(i // 8) / 100)
        time.sleep(0.01)

      time.sleep(1)
      con.clear()

  directionChangeMap = {
      '1': SnakeGame.UP,
      '2': SnakeGame.DOWN,
      '3': SnakeGame.LEFT,
      '4': SnakeGame.RIGHT,

  }

  loop.run()


gamestart()
