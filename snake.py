import pygame
import numpy as np

SCREEN_WIDTH = 900
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

GAME_WIDTH = 600
GAME_HEIGHT = 600
WIDTH = 30
SIZE = GAME_WIDTH // WIDTH

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

    def increase_size(self, food) :
        head = (food.i, food.j)
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

def pos_food_to_snake(snake, food) :
    head = snake.arr[0]
    
    if food.j < head[1] :
        if food.i < head[0] :
            pos = 0
        elif food.i == head [0] :
            pos = 1
        else :
            pos = 2
    elif food.j == head[1] :
        if food.i < head[0] :
            pos = 3
        elif food.i == head[0] :
            pos = 4
        else :
            pos = 5
    else :
        if food.i < head[0] :
            pos = 6
        elif food.i == head[0] :
            pos = 7
        else :
            pos = 8

    return pos

def snake_view(snake) :
    head = snake.arr[0]

    up = 0
    down = 0
    left = 0
    right = 0

    # walls - 
    if head[0] == 0 :
        left = 1
    elif head[0] == SIZE - 1 :
        right = 1
    if head[1] == 0 :
        up = 1
    elif head[1] == SIZE - 1 :
        down = 1

    for i in range(len(snake.arr)) :
        node = snake.arr[i]

        if head[0] - node[0] == 1 and head[1] == node[1] :
            left = 1
        if head[0] - node[0] == -1 and head[1] == node[1] :
            right = 1
        if head[1] - node[1] == 1 and head[0] == node[0] :
            up = 1
        if head[1] - node[1] == -1 and head[0] == node[0] :
            down = 1

    return (up, down, left, right)

def find_view_index(view_index) :
    mult = 1
    ans = 0
    for ele in view_index :
        ans += ele * mult
        mult *= 2

    return ans

def find_dist(snake, food) :
    head = snake.arr[0]
    return (head[0] - food.i) ** 2 + (head[1] - food.j) ** 2

DIR_CHOICES = [(0, -1), (0, 1), (-1, 0), (1, 0)]
# dir_choice = np.random.randint(0, 4)

LEARNING_RATE = 0.1
DISCOUNT = 0.9
EPISODES = 500
MAX_FRAME_COUNT = 1000 

epsilon = 1
EPSILON_DECAY = 2 / EPISODES

FOOD_REWARD = 30
DEATH_PENALTY = -100
TIME_PENALTY = -1
TOWARDS_FOOD = 1
AWAY_FROM_FOOD = -1

prev_record = 0
last_10 = [1] * 10

q_table = np.random.uniform(low = -10, high = 0, size = ((9, 16, 4)))

for episode in range(EPISODES):
    snake = Snake()
    food = Food(snake)

    run = True
    render = True    
    delay = False
    DELAY_TIME = 50

    action = np.random.randint(0, 4)
    
    prev_dist = find_dist(snake, food)

    framecount = 0
    while run and framecount < MAX_FRAME_COUNT:

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

        pos_food = pos_food_to_snake(snake, food)
        view_snake = snake_view(snake)
        view_index = find_view_index(view_snake)

        if render :
            win.fill(BLACK)
            pygame.draw.rect(win, WHITE, (GAME_WIDTH, 0, SCREEN_WIDTH - GAME_WIDTH, SCREEN_HEIGHT))

            font = pygame.font.SysFont('Consolas', 25)

            text = font.render('Episode : ' + str(episode), True, BLACK)
            win.blit(text, (GAME_WIDTH + 10, 20))

            text = font.render('Length : ' + str(snake.length), True, BLACK)
            win.blit(text, (GAME_WIDTH + 10, 50))

            text = font.render('Epsilon : ' + str(format(epsilon, '.3f')), True, BLACK)
            win.blit(text, (GAME_WIDTH + 10, 80))

            text = font.render('Record length : ' + str(prev_record), True, BLACK)
            win.blit(text, (GAME_WIDTH + 5, 140))

            font = pygame.font.SysFont('Consolas', 20)

            text = font.render('Last 10 Avg : ' + str(sum(last_10)//10), True, BLACK)
            win.blit(text, (GAME_WIDTH + 5, 170))

            text = font.render('AI Agent Observation State -', True, BLACK)
            win.blit(text, (GAME_WIDTH + 5, 240))

            text = font.render('Position of Apple', True, BLACK)
            win.blit(text, (GAME_WIDTH + 5, 275))

            text = font.render('Obstacles surrounding head', True, BLACK)
            win.blit(text, (GAME_WIDTH + 5, 460))

            W = 30
            BOX_SEP = W + 5
            START_X = (GAME_WIDTH + SCREEN_WIDTH) // 2 - BOX_SEP * 3 // 2
            START_Y = SCREEN_HEIGHT // 2 
            pos = 0
            for j in range(3) :
                for i in range(3) :
                    if pos != 4 :
                        
                        color = BLACK
                        if pos == pos_food :
                            color = RED

                        pygame.draw.rect(win, color, (START_X + i * BOX_SEP, START_Y + j * BOX_SEP, W, W))
                
                    pos += 1

            
            W = 30
            BOX_SEP = W + 5
            START_X = (GAME_WIDTH + SCREEN_WIDTH) // 2 - BOX_SEP * 3 // 2
            START_Y = SCREEN_HEIGHT // 2 + BOX_SEP * 11 // 2
            for i in range(4) :
                color = BLACK
                if view_snake[i] == 1 :
                    color = GRAY

                if i == 0 :
                    pygame.draw.rect(win, color, (START_X + BOX_SEP, START_Y, W, W))
                elif i == 1 :
                    pygame.draw.rect(win, color, (START_X + BOX_SEP, START_Y + 2 * BOX_SEP, W, W))
                elif i == 2 :
                    pygame.draw.rect(win, color, (START_X, START_Y + BOX_SEP, W, W))
                elif i == 3 :
                    pygame.draw.rect(win, color, (START_X + 2 * BOX_SEP, START_Y + BOX_SEP, W, W))

        curr_state = (pos_food, view_index)

        prev_action = action
        if np.random.random() > epsilon :
            action = np.argmax(q_table[curr_state])
        else :
            action = np.random.randint(0, 4)

        if (action == 1 and prev_action == 0) or (action == 0 and prev_action == 1) :
            action = prev_action 
        elif (action == 2 and prev_action == 3) or (action == 3 and prev_action == 2) :
            action = prev_action
            
        dir_choice = action
        snake.move(DIR_CHOICES[dir_choice])

        next_state = (pos_food, view_index)
        # reward = TIME_PENALTY
        curr_dist = find_dist(snake, food)

        if curr_dist < prev_dist :
            reward = TOWARDS_FOOD
        else :
            reward = AWAY_FROM_FOOD

        prev_dist = curr_dist
        if snake.length > prev_record :
            prev_record = snake.length
            delay = True

        eating = False
        if snake.eat(food) :
            eating = True
            snake.increase_size(food)
            food.spawn(snake)
            reward = FOOD_REWARD
            framecount = 0

        if snake.touch_wall() :
            run = False
            reward = DEATH_PENALTY

        if snake.bite() and not eating :
            run = False
            reward = DEATH_PENALTY

        max_future_q = np.max(q_table[next_state])
        current_q = q_table[curr_state][action]

        new_q = (1 - LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
        q_table[curr_state][action] = new_q

        curr_state = next_state

        if render and run :
            food.display()
            snake.display()
            pygame.display.update()

        framecount += 1

    if epsilon > 0 :
        epsilon -= EPSILON_DECAY

    last_10.pop(0)
    last_10.append(snake.length)

pygame.quit()