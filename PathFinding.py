from tkinter import messagebox, Tk
import pygame
import sys
import random
from queue import PriorityQueue


window_width = 800
window_height = 800

window = pygame.display.set_mode((window_width+300, window_height))

columns = 50
rows = 50

box_width = window_width // columns
box_height = window_height // rows

#module import
pygame.init()


class Button():
    def __init__(self, x, y, image, text, scale, t_scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(
            image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.text = text.upper()
        self.t_scale = t_scale

    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()
        font = pygame.font.SysFont('cambria', self.t_scale)
        text = font.render(self.text, True, (255, 255, 255))

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button on screen
        window.blit(self.image, (self.rect.x, self.rect.y))
        window.blit(text, (self.rect.x + 1, self.rect.y + 1))

        return action


class Box:
    def __init__(self, i, j):
        self.x = i
        self.y = j
        self.start = False
        self.wall = False
        self.target = False
        self.queued = False
        self.visited = False
        self.neighbours = []
        self.prior = None

    def draw(self, win, color):
        pygame.draw.rect(win, color, (self.x * box_width,
                         self.y * box_height, box_width-2, box_height-2))

    def set_neighbours(self):
        if self.x > 0 and not grid[self.x-1][self.y].wall:#Left 
            self.neighbours.append(grid[self.x - 1][self.y])
        if self.x < columns - 1 and not grid[self.x + 1][self.y].wall:#right
            self.neighbours.append(grid[self.x + 1][self.y])
        if self.y > 0 and not grid[self.x][self.y - 1].wall:#Top
            self.neighbours.append(grid[self.x][self.y - 1])
        if self.y < rows - 1 and not grid[self.x][self.y + 1].wall:#Bottom
            self.neighbours.append(grid[self.x][self.y + 1])


# Initializing
grid = []
queue = []
path = []

# Create Grid
for i in range(columns):
    arr = []
    for j in range(rows):
        arr.append(Box(i, j))
    grid.append(arr)


# load button images
frame_img = pygame.image.load('frame.jpeg')

# Buttons
exit_button = Button(window_width+115, 750, frame_img, 'exit', 0.2, 18)
reset_button = Button(window_width+80, 50, frame_img, 'Reset', 0.2, 18)
random_button = Button(window_width+150, 50, frame_img, 'Maze', 0.2, 18)
diji_button = Button(window_width+80, 130, frame_img, 'Diji', 0.2, 18)
A_star_button = Button(window_width+150, 130, frame_img, 'A*', 0.2, 20)

# Manhattan distance
def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)

def draw_win(toggle_wall):
    window.fill((202, 228, 241))

    for i in range(columns):
        for j in range(rows):
            box = grid[i][j]
            box.draw(window, (100, 100, 100))

            if not box.wall:
                box.draw(window, (100, 100, 100))
            if not box.target:
                box.draw(window, (100, 100, 100))
            if box.wall:
                box.draw(window, (10, 10, 10))
            if box.queued:
                box.draw(window, (200, 0, 0))
            if box.visited:
                box.draw(window, (0, 200, 0))
            if box in path:
                box.draw(window, (0, 0, 200))
            if box.start:
                box.draw(window, (0, 100, 100))
            if box.target:
                box.draw(window, (200, 200, 0))

    # Text
    Font_t = pygame.font.SysFont('timesnewroman',  15)
    text = Font_t.render("Toggle State :", False, (0, 0, 0), (202, 228, 241))
    window.blit(text, (window_width+80, 100))

    # State of Toggle
    if toggle_wall == True:
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(
            window_width+170, 105, 10, 10))
    if toggle_wall == False:
        pygame.draw.rect(window, (0, 0, 0), pygame.Rect(
            window_width+170, 105, 10, 10),  2)

    # start_button.draw()
    exit_button.draw()
    reset_button.draw()
    random_button.draw()
    diji_button.draw()
    A_star_button.draw()

    pygame.display.update()


def dijikastra(start_box, target_box, toggle_wall):
    searching = True
    while searching:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if len(queue) > 0 and searching:
            current_box = queue.pop(0)
            current_box.visited = True
            if current_box == target_box:
                searching = False
                while current_box.prior != start_box:# Back tracking
                    path.append(current_box.prior)
                    current_box = current_box.prior
                else:
                    Tk().wm_withdraw()
                    messagebox.showinfo(
                        'Solution Found!', "Distance from origin is {}".format(len(path)+1))

            else:
                for neighbour in current_box.neighbours:
                    if not neighbour.queued and not neighbour.wall:
                        neighbour.queued = True
                        neighbour.prior = current_box
                        queue.append(neighbour)
        else:
            if searching:
                Tk().wm_withdraw()
                messagebox.showinfo("No Solution", "There is no solution!")
                searching = False
    # Here goes the Painting of our Window.
        draw_win(toggle_wall)
    return True


def A_star(start_box, target_box, toggle_wall):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start_box))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start_box] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start_box] = h((start_box.x, start_box.y), (target_box.x, target_box.y))

    open_set_hash = {start_box}

    while not open_set.empty():
        #For Quiting the code
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == target_box:
            while current in came_from:
                path.append(current)
                current = came_from[current]
            else:
                Tk().wm_withdraw()
                messagebox.showinfo(
                    'Solution Found!', "Distance from origin is {}".format(len(path)))
            return True

        for neighbor in current.neighbours:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h((neighbor.x, neighbor.y), (target_box.x, target_box.y))
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.queued = True

        draw_win(toggle_wall)

        if current != start_box:
            current.visited =True
    else:
        Tk().wm_withdraw()
        messagebox.showinfo("No Solution", "There is no solution!")
        return True

def main():
    begin_search_diji = False
    begin_search_astar = False
    target_box_set = False
    stop_algo = False
    target_box = None
    start_box = None
    start_box_set = False
    toggle_wall = False

    while True:
        for event in pygame.event.get():
            # Quit Window
            if event.type == pygame.QUIT or exit_button.draw():
                pygame.quit()
                sys.exit()
            # Mouse Controls
            elif event.type == pygame.MOUSEMOTION:
                x = pygame.mouse.get_pos()[0]
                y = pygame.mouse.get_pos()[1]
                
                #Random Walls in the window (MAZE)
                if random_button.draw() and (not begin_search_diji or not begin_search_astar):
                    #random no of box walls
                    r_range_x = random.randrange(10,30)
                    r_range_y = random.randrange(10,30)
                    for i in range(r_range_x):
                        for j in range(r_range_y):
                            #random place to put
                            r_i = random.randrange(50)
                            r_j = random.randrange(50)
                            if not grid[r_i][r_j].start and not grid[r_i][r_j].target:
                                grid[r_i][r_j].wall = True

                
                
                #Reset every thing
                if reset_button.draw() and (not begin_search_diji or not begin_search_astar):
                    toggle_wall = False
                    target_box_set = False
                    start_box_set = False
                    for i in range(columns):
                        for j in range(rows):
                            grid[i][j].wall = False
                            grid[i][j].target = False
                            grid[i][j].start = False
                            grid[i][j].visited = False
                            
                
                # Draw Wall
                if x > window_width-1 or x < 0 or y > window_height-1 or y < 0:
                    continue
                i = x // box_width
                j = y // box_height
                if event.buttons[0] and not toggle_wall:
                    grid[i][j].wall = True
                if event.buttons[0] and toggle_wall:
                    grid[i][j].wall = False

                    
                # Set Start/Target
                if event.buttons[2] and not toggle_wall:
                    target_box = grid[i][j]
                    if not target_box.wall and not target_box.target and not start_box_set:
                        start_box = target_box
                        start_box.start = True
                        start_box_set = True
                        start_box.visited = True
                        queue.append(start_box)
                    if not target_box.wall and not target_box.start and not target_box_set:
                        target_box.target = True
                        target_box_set = True
                if event.buttons[2] and toggle_wall:
                    target_box = grid[i][j]
                    target_box.target = False
                    target_box_set = False
                    
                    
                        
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t and toggle_wall == False:
                    toggle_wall = True
                else:
                    toggle_wall = False
                    
                    
            # Start Algorithm
            if target_box_set:
                # Set Neighbours
                for i in range(columns):
                    for j in range(rows):
                        grid[i][j].set_neighbours()
                if diji_button.draw():
                    begin_search_diji = True
                if A_star_button.draw():
                    begin_search_astar = True
                    

                
        # Here Starts the Dijikastra algorithm
        if begin_search_diji and not stop_algo:
            stop_algo = dijikastra(start_box, target_box, toggle_wall)

        # Here Starts the A* algorithm
        if begin_search_astar and not stop_algo:
            stop_algo = A_star(start_box,target_box, toggle_wall)


        # Here goes the Painting of our Window.
        draw_win(toggle_wall)
main()
