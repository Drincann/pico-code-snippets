import random


from Scheduler import Timer


class SnakeGame:
  # map
  WALL = 0
  EMPTY = 1

  # row col
  UP = (-1, 0)
  DOWN = (1, 0)
  LEFT = (0, -1)
  RIGHT = (0, 1)

  # state
  GAMEOVER = 1
  RUNNING = 2

  def __init__(self,
               map: list[list[int]], snake: list[tuple[int, int]],
               speed: float = 1, direction: tuple[int, int] = UP
               ) -> None:
    self.map = map
    self.snake = snake
    self.wallSet = set()
    for row in range(len(map)):
      for col in range(len(map[row])):
        if map[row][col] == SnakeGame.WALL:
          self.wallSet.add((row, col))
    self.food = None

    self.speed = speed
    self.direction = direction
    self.nextDirection = direction

  def begin(self, callback) -> None:
    self.callback = callback
    self.food = self.__genFood()
    self.callback(SnakeGame.RUNNING, self.wallSet, self.snake, self.food)
    Timer.setTimeout(int(1/self.speed * 1000), self.__loop)

  def __genFood(self):
    food = (random.randint(
        0, len(self.map[0]) - 1), random.randint(0, len(self.map) - 1)
    )
    while food in self.snake or food in self.wallSet:
      food = (random.randint(
          0, len(self.map[0]) - 1), random.randint(0, len(self.map) - 1)
      )
    return food

  def changeDirection(self, direction: tuple[int, int]) -> None:
    if direction == self.direction \
            or direction == SnakeGame.UP and self.direction == SnakeGame.DOWN \
            or direction == SnakeGame.DOWN and self.direction == SnakeGame.UP \
            or direction == SnakeGame.LEFT and self.direction == SnakeGame.RIGHT \
            or direction == SnakeGame.RIGHT and self.direction == SnakeGame.LEFT:
      return
    self.nextDirection = direction

  def __loop(self):
    self.direction = self.nextDirection
    # check the direction is valid
    newHead = (self.snake[-1][0] + self.direction[0],
               self.snake[-1][1] + self.direction[1])

    if newHead in self.wallSet or newHead in self.snake:
      self.callback(SnakeGame.GAMEOVER, self.wallSet, self.snake, self.food)
      return
    # check the food
    if self.food == newHead:
      self.snake.append(newHead)
      self.food = self.__genFood()
    else:
      self.snake.pop(0)
      self.snake.append(newHead)
    self.callback(SnakeGame.RUNNING, self.wallSet, self.snake, self.food)
    Timer.setTimeout(int(1/self.speed * 1000), self.__loop)
