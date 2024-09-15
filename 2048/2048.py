import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 4
CELL_SIZE = 100
MARGIN = 10
WIDTH = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN
HEIGHT = WIDTH + 100  # Extra space for score and buttons
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_CELL_COLOR = (205, 193, 180)
FONT = pygame.font.Font(None, 36)
LARGE_FONT = pygame.font.Font(None, 48)

# Color scheme for tiles
COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

class Game2048:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.best_score = self.load_best_score()
        self.game_over = False
        self.add_new_tile()
        self.add_new_tile()

    def load_best_score(self):
        try:
            with open("best_score.txt", "r") as f:
                return int(f.read())
        except FileNotFoundError:
            return 0

    def save_best_score(self):
        with open("best_score.txt", "w") as f:
            f.write(str(self.best_score))

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def move(self, direction):
        moved = False
        if direction == "UP":
            for j in range(GRID_SIZE):
                column = [self.grid[i][j] for i in range(GRID_SIZE) if self.grid[i][j] != 0]
                column = self.merge(column)
                for i in range(GRID_SIZE):
                    value = column[i] if i < len(column) else 0
                    if self.grid[i][j] != value:
                        moved = True
                    self.grid[i][j] = value
        elif direction == "DOWN":
            for j in range(GRID_SIZE):
                column = [self.grid[i][j] for i in range(GRID_SIZE-1, -1, -1) if self.grid[i][j] != 0]
                column = self.merge(column)
                for i in range(GRID_SIZE-1, -1, -1):
                    value = column[GRID_SIZE-1-i] if GRID_SIZE-1-i < len(column) else 0
                    if self.grid[i][j] != value:
                        moved = True
                    self.grid[i][j] = value
        elif direction == "LEFT":
            for i in range(GRID_SIZE):
                row = [self.grid[i][j] for j in range(GRID_SIZE) if self.grid[i][j] != 0]
                row = self.merge(row)
                for j in range(GRID_SIZE):
                    value = row[j] if j < len(row) else 0
                    if self.grid[i][j] != value:
                        moved = True
                    self.grid[i][j] = value
        elif direction == "RIGHT":
            for i in range(GRID_SIZE):
                row = [self.grid[i][j] for j in range(GRID_SIZE-1, -1, -1) if self.grid[i][j] != 0]
                row = self.merge(row)
                for j in range(GRID_SIZE-1, -1, -1):
                    value = row[GRID_SIZE-1-j] if GRID_SIZE-1-j < len(row) else 0
                    if self.grid[i][j] != value:
                        moved = True
                    self.grid[i][j] = value
        if moved:
            self.add_new_tile()
            if self.is_game_over():
                self.game_over = True
            if self.score > self.best_score:
                self.best_score = self.score
                self.save_best_score()

    def merge(self, line):
        for i in range(len(line) - 1):
            if line[i] == line[i + 1]:
                line[i] *= 2
                self.score += line[i]
                line.pop(i + 1)
                line.append(0)
        return line

    def is_game_over(self):
        if any(0 in row for row in self.grid):
            return False
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                value = self.grid[i][j]
                if (i < GRID_SIZE-1 and value == self.grid[i+1][j]) or \
                   (j < GRID_SIZE-1 and value == self.grid[i][j+1]):
                    return False
        return True

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                value = self.grid[i][j]
                color = COLORS.get(value, COLORS[0])
                pygame.draw.rect(self.screen, color, (j*(CELL_SIZE+MARGIN)+MARGIN, i*(CELL_SIZE+MARGIN)+MARGIN, CELL_SIZE, CELL_SIZE))
                if value != 0:
                    text = FONT.render(str(value), True, (0, 0, 0))
                    text_rect = text.get_rect(center=(j*(CELL_SIZE+MARGIN)+MARGIN+CELL_SIZE//2, i*(CELL_SIZE+MARGIN)+MARGIN+CELL_SIZE//2))
                    self.screen.blit(text, text_rect)
        
        score_text = FONT.render(f"Score: {self.score}", True, (0, 0, 0))
        best_score_text = FONT.render(f"Best: {self.best_score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, HEIGHT - 90))
        self.screen.blit(best_score_text, (WIDTH - best_score_text.get_width() - 10, HEIGHT - 90))

        if self.game_over:
            game_over_text = LARGE_FONT.render("Game Over!", True, (0, 0, 0))
            self.screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - game_over_text.get_height()//2))

        pygame.draw.rect(self.screen, (150, 150, 150), (10, HEIGHT - 50, 100, 40))
        restart_text = FONT.render("Restart", True, (0, 0, 0))
        self.screen.blit(restart_text, (20, HEIGHT - 45))

        pygame.draw.rect(self.screen, (150, 150, 150), (WIDTH - 110, HEIGHT - 50, 100, 40))
        quit_text = FONT.render("Quit", True, (0, 0, 0))
        self.screen.blit(quit_text, (WIDTH - 90, HEIGHT - 45))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_UP:
                        self.move("UP")
                    elif event.key == pygame.K_DOWN:
                        self.move("DOWN")
                    elif event.key == pygame.K_LEFT:
                        self.move("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        self.move("RIGHT")
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if HEIGHT - 50 < y < HEIGHT - 10:
                        if 10 < x < 110:
                            self.reset_game()
                        elif WIDTH - 110 < x < WIDTH - 10:
                            running = False

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game2048()
    game.run()