import pygame
import sys
import random
import time

pygame.init()
WIDTH, HEIGHT = 800, 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Letter Maze Escape Game")
clock = pygame.time.Clock()

WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
RED = (255,0,0)
PURPLE = (200,0,255)

font_ui = pygame.font.SysFont("Arial", 40)
font_small = pygame.font.SysFont("Arial", 25)

# ---------------- FULL KEYBOARD INPUT ----------------
def get_letter_input():
    text_input = ""

    while True:
        screen.fill(WHITE)

        title = font_ui.render("Type Any One Character:", True, BLACK)
        typed = font_ui.render(text_input, True, BLACK)
        hint = font_small.render("Press ENTER to confirm", True, BLACK)

        screen.blit(title, (200, 300))
        screen.blit(typed, (350, 380))
        screen.blit(hint, (260, 450))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and text_input:
                    return text_input[0]   # take first character only
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    if event.unicode.isprintable():
                        text_input += event.unicode

# ---------------- MODE SELECT ----------------
def get_difficulty():
    options = {
        "E": {"cell": 12, "randomness": 0.12, "mode": "Explorer"},
        "A": {"cell": 10, "randomness": 0.05, "mode": "Adventurer"},
        "M": {"cell": 8,  "randomness": 0.01, "mode": "Master"}
    }

    while True:
        screen.fill(WHITE)

        t1 = font_ui.render("Select Mode:", True, BLACK)
        t2 = font_ui.render("E = Explorer  A = Adventurer  M = Master", True, BLACK)

        screen.blit(t1, (250, 300))
        screen.blit(t2, (50, 380))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                key = event.unicode.upper()
                if key in options:
                    return options[key]

# ---------------- LETTER MASK ----------------
def generate_letter_mask(letter, CELL):
    font = pygame.font.SysFont("Arial", 600, bold=True)
    text_surface = font.render(letter, True, BLACK)
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))

    temp = pygame.Surface((WIDTH, HEIGHT))
    temp.fill(WHITE)
    temp.blit(text_surface, text_rect)

    mask = [[0 for _ in range(WIDTH//CELL)] for _ in range(HEIGHT//CELL)]

    for y in range(0, HEIGHT, CELL):
        for x in range(0, WIDTH, CELL):

            black = 0
            total = 0

            for dy in range(CELL):
                for dx in range(CELL):
                    px = min(x+dx, WIDTH-1)
                    py = min(y+dy, HEIGHT-1)

                    if temp.get_at((px,py)) == BLACK:
                        black += 1
                    total += 1

            if black / total > 0.2:
                mask[y//CELL][x//CELL] = 1

    return mask

# ---------------- MAZE ----------------
def generate_maze(mask, randomness):
    rows, cols = len(mask), len(mask[0])
    maze = [[1]*cols for _ in range(rows)]

    def neighbors(x,y):
        dirs = [(2,0),(-2,0),(0,2),(0,-2)]
        res = []
        for dx,dy in dirs:
            nx,ny = x+dx, y+dy
            if 0<=nx<cols and 0<=ny<rows and mask[ny][nx]:
                res.append((nx,ny,dx,dy))
        return res

    start = None
    for y in range(rows):
        for x in range(cols):
            if mask[y][x]:
                start=(x,y)
                break
        if start:
            break

    stack=[start]
    maze[start[1]][start[0]]=0

    while stack:
        x,y = stack[-1]
        nbs = [n for n in neighbors(x,y) if maze[n[1]][n[0]]==1]

        if nbs and random.random() > randomness:
            nx,ny,dx,dy = random.choice(nbs)
            maze[y+dy//2][x+dx//2]=0
            maze[ny][nx]=0
            stack.append((nx,ny))
        else:
            stack.pop()

    return maze

# ---------------- DISTANCE ----------------
def dist(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ---------------- MONSTER SPAWN ----------------
def spawn_monster_far():
    candidates = []
    for y in range(rows):
        for x in range(cols):
            if maze[y][x]==0:
                candidates.append((x,y))

    candidates.sort(key=lambda p: dist(player,p), reverse=True)
    safe_zone = candidates[:max(1,len(candidates)//10)]
    return list(random.choice(safe_zone))

# ---------------- GAME START ----------------
letter = get_letter_input()
diff = get_difficulty()

CELL = diff["cell"]
RANDOMNESS = diff["randomness"]
MODE = diff["mode"]

mask = generate_letter_mask(letter, CELL)
maze = generate_maze(mask, RANDOMNESS)

rows, cols = len(maze), len(maze[0])

# player start
player = None
for y in range(rows):
    for x in range(cols):
        if maze[y][x]==0:
            player=[x,y]
            break
    if player:
        break

# exit
exit_pos = None
maxd = -1
for y in range(rows):
    for x in range(cols):
        if maze[y][x]==0:
            d = dist(player,(x,y))
            if d > maxd:
                maxd = d
                exit_pos=[x,y]

# monster only in master
monster = None
if MODE == "Master":
    monster = spawn_monster_far()

start_time = time.time()

# ---------------- GAME LOOP ----------------
running = True
win = False
lose = False
elapsed = 0

while running:
    screen.fill(WHITE)

    elapsed = int(time.time() - start_time)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    new = player.copy()

    if keys[pygame.K_UP]: new[1]-=1
    if keys[pygame.K_DOWN]: new[1]+=1
    if keys[pygame.K_LEFT]: new[0]-=1
    if keys[pygame.K_RIGHT]: new[0]+=1

    if 0<=new[0]<cols and 0<=new[1]<rows and maze[new[1]][new[0]]==0:
        player=new

    # monster movement
    if MODE == "Master" and monster:
        if monster[0]<player[0]: monster[0]+=1
        elif monster[0]>player[0]: monster[0]-=1
        if monster[1]<player[1]: monster[1]+=1
        elif monster[1]>player[1]: monster[1]-=1

        if monster == player:
            lose = True
            running = False

    # draw maze
    for y in range(rows):
        for x in range(cols):
            if maze[y][x]==1:
                pygame.draw.rect(screen, BLACK,(x*CELL,y*CELL,CELL,CELL))

    pygame.draw.rect(screen, GREEN,(player[0]*CELL,player[1]*CELL,CELL,CELL))
    pygame.draw.rect(screen, RED,(exit_pos[0]*CELL,exit_pos[1]*CELL,CELL,CELL))

    if MODE == "Master":
        pygame.draw.rect(screen, PURPLE,(monster[0]*CELL,monster[1]*CELL,CELL,CELL))

    # win check
    if player == exit_pos:
        win = True
        running = False

    # timer UI
    pygame.draw.rect(screen, BLACK, (5,5,160,40), border_radius=8)
    timer_text = font_small.render(f"Time: {elapsed}s", True, WHITE)
    screen.blit(timer_text, (15,10))

    pygame.display.flip()
    clock.tick(20)

# ---------------- END SCREEN ----------------
screen.fill(WHITE)

if win:
    msg = "Victory: You conquered the maze!"
elif lose:
    msg = "Game Over: The monster caught you!"
else:
    msg = "Game Ended"

text = font_ui.render(msg, True, BLACK)
screen.blit(text, (60, 350))

time_text = font_ui.render(f"Final Time: {elapsed}s", True, BLACK)
screen.blit(time_text, (200, 420))

pygame.display.flip()
pygame.time.wait(4000)

pygame.quit()
sys.exit()