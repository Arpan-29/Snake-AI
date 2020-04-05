import pygame
import numpy as np

from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake')

pygame.font.init()
font = pygame.font.SysFont('Consolas', 25)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)

WIDTH = 30
SIZE = SCREEN_WIDTH // WIDTH

class Snake :
    def __init__(self) :
        self.arr = []
        head = (np.random.randint(1, SIZE - 1), np.random.randint(1, SIZE - 1))
        self.arr.append(head)
        self.length = 1

    def move(self, dir) :        
        head = (self.arr[0][0] + dir[0], self.arr[0][1] + dir[1])
        self.arr.insert(0, head)
        self.arr.pop()

    def eat(self, food) :
        head = self.arr[0]
        return head[0] == food.i and head[1] == food.j

    def increase_size(self) :
        head = self.arr[0]
        self.arr.insert(0, head)
        self.length += 1

    def touch_wall(self) :
        head = self.arr[0]
        if head[0] < 0 or head[0] > SIZE - 1 or head[1] < 0 or head[1] > SIZE - 1 :
            return True 
        
        return False

    def bite(self) :
        head = self.arr[0]
        for i in range(1, len(self.arr)) :
            node = self.arr[i]

            if head[0] == node[0] and head[1] == node[1] :
                return True

        return False    

    def display(self) :
        for i in range(len(self.arr)) :
            node = self.arr[i]

            pygame.draw.rect(win, BLACK, (node[0] * WIDTH, node[1] * WIDTH, WIDTH, WIDTH))
            pygame.draw.rect(win, GREEN, (node[0] * WIDTH + 1, node[1] * WIDTH + 1, WIDTH - 1, WIDTH - 1))

            if i == 0 :
                pygame.draw.circle(win, BLACK, 
                                  (node[0] * WIDTH + WIDTH // 2, 
                                   node[1] * WIDTH + WIDTH // 2), 
                                   WIDTH // 10)

class Food :
    def __init__(self, snake) :
        self.spawn(snake) 
        
    def spawn(self, snake) :
        
        coord = snake.arr[0]
        while coord in snake.arr :
            self.i = np.random.randint(0, SIZE)
            self.j = np.random.randint(0, SIZE)
            coord = (self.i, self.j)
        
    def display(self) :
        pygame.draw.rect(win, RED, (self.i * WIDTH, self.j * WIDTH, WIDTH, WIDTH))

def get_choice(path) :
    if len(path) <= 1 :
        return None, path

    start = path[0]
    Next = path[1]

    path.pop(0)

    if start[1] - Next[1] == 1 :
        return 0, path
    elif start[1] - Next[1] == -1 :
        return 1, path    
    elif start[0] - Next[0] == 1 :
        return 2, path
    else :
        return 3, path

def isSafe(mat, snake, dir_choice) :
    head = snake.arr[0]
    dir = DIR_CHOICES[dir_choice]
    i = head[0] + dir[0]
    j = head[1] + dir[1]

    if i < 0 or i > SIZE - 1 or j < 0 or j > SIZE - 1 :
        return False

    if mat[j][i] == 0 :
        return False
    
    return True

DIR_CHOICES = [(0, -1), (0, 1), (-1, 0), (1, 0)]
dir_choice = np.random.randint(0, 4)

snake = Snake()
food = Food(snake)

run = True
start = False
render = True    
delay = True
DELAY_TIME = 10

finder = AStarFinder()
path = []
ate = False

while run :

    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            run = False

    if delay :
        pygame.time.delay(DELAY_TIME)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE] :
        quit() 
    elif keys[pygame.K_SPACE] :
        pygame.time.delay(100)
        if not start :
            start = True
        else :
            delay = not delay
    elif keys[pygame.K_UP] :
        if dir_choice != 1 :
            dir_choice = 0
    elif keys[pygame.K_DOWN] :
        if dir_choice != 0 :
            dir_choice = 1
    elif keys[pygame.K_LEFT] :
        if dir_choice != 3 :
            dir_choice = 2
    elif keys[pygame.K_RIGHT] :
        if dir_choice != 2 :
            dir_choice = 3

    if start :
        if render :
            win.fill(BLACK)   

        survival_mode = False
        if len(path) > 0 :
            head = snake.arr[0]
            dir_choice, path = get_choice(path)

            if dir_choice is None :
                survival_mode = True
            else :
                survival_mode = False
        else :
            survival_mode = True
        
        if survival_mode :
            mat = []
            for i in range(SIZE) :
                row = []
                for j in range(SIZE) :
                    row.append(1)
                mat.append(row)

            for ele in snake.arr :
                mat[ele[1]][ele[0]] = 0

            dir_choice = np.random.randint(0, 4)
            while not isSafe(mat, snake, dir_choice) :
                dir_choice = np.random.randint(0, 4)

        snake.move(DIR_CHOICES[dir_choice])

        ate = False
        if snake.eat(food) :
            ate = True
            food.spawn(snake)
            snake.increase_size()
            path = []

        if snake.touch_wall() :
            print('TOUCH WALL')
            run = False

        if snake.bite() and not ate:
            print('BITE ITSELF')
            run = False

        if render :
            food.display()
            snake.display()
            pygame.display.update() 

        if len(path) == 0 :
            mat = []
            for i in range(SIZE) :
                row = []
                for j in range(SIZE) :
                    row.append(1)
                mat.append(row)

            for ele in snake.arr :
                mat[ele[1]][ele[0]] = 0

            grid = Grid(matrix=mat)   

            head = snake.arr[0]

            start = grid.node(head[0], head[1])
            end = grid.node(food.i, food.j)

            path, runs = finder.find_path(start, end, grid)

pygame.quit()
print(grid.grid_str(path=path, start=start, end=end))