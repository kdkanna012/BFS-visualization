import pygame
from collections import deque
from queue import PriorityQueue

WIDTH = 750
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Algorithm")


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:

    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.colour = WHITE
        self.width = width
        self.total_rows = total_rows
        self.x = row * width
        self.y = col * width
        self.neighbours = []

    def is_open(self):
        return self.colour == GREEN

    def is_closed(self):
        return self.colour == RED

    def is_barrier(self):
        return self.colour == BLACK

    def is_start(self):
        return self.colour == ORANGE

    def is_end(self):
        return self.colour == TURQUOISE

    def reset(self):
        self.colour = WHITE

    def make_open(self):
        self.colour = GREEN

    def make_closed(self):
        self.colour = RED

    def make_barrier(self):
        self.colour = BLACK

    def make_start(self):
        self.colour = ORANGE

    def make_end(self):
        self.colour = TURQUOISE

    def make_path(self):
        self.colour = PURPLE

    def get_pos(self):
        return self.row, self.col

    def update_neighbours(self, grid):
        self.neighbours = []

        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():
            self.neighbours.append(grid[self.row-1][self.col])

        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_barrier():
            self.neighbours.append(grid[self.row+1][self.col])

        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():
            self.neighbours.append(grid[self.row][self.col-1])

        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_barrier():
            self.neighbours.append(grid[self.row][self.col+1])

    def draw(self, win):
        pygame.draw.rect(win, self.colour,
                         (self.x, self.y, self.width, self.width))

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, end, draw):
    current = end
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def bfs(draw, grid, start, end):
    queue = deque([start])
    visited = set()
    came_from = {}

    while len(queue) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = queue.popleft()
        visited.add(start)
        if current == end:
            reconstruct_path(came_from, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbour in current.neighbours:
            if neighbour not in visited:
                queue.append(neighbour)
                came_from[neighbour] = current
                visited.add(neighbour)
                neighbour.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def dijkstra(draw, grid, start, end):
    queue = PriorityQueue()
    queue.put((0, start))
    visited = set()
    distance = {node: float('inf') for row in grid for node in row}
    distance[start] = 0
    came_from = {}

    while queue.qsize() > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        cdist, current = queue.get()
        visited.add(start)

        if current == end:
            reconstruct_path(came_from, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbour in current.neighbours:
            if neighbour not in visited:
                ndist = cdist + 1
                if ndist < distance[neighbour]:
                    distance[neighbour] = ndist
                    queue.put((ndist, neighbour))
                    came_from[neighbour] = current
                    visited.add(neighbour)
                    neighbour.make_open()

        draw()

        if current != start:
            current.make_closed()


def make_grid(rows, width):
    gap = width // rows
    grid = []

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]

                if not start and node != end:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != start and node != end:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()

                if node == start:
                    start = None

                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)

                    dijkstra(lambda: draw(win, grid, ROWS, width),
                             grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)
