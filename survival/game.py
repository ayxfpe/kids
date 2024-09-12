import pygame
import random

# Initialize Pygame
pygame.init()

# Grid settings
GRID_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 15

# Set up the display
WIDTH = GRID_SIZE * GRID_WIDTH
HEIGHT = GRID_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Survival Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
GRAY = (100, 100, 100)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)

class Player:
    def __init__(self):
        self.x = GRID_WIDTH // 2
        self.y = GRID_HEIGHT - 2
        self.health = 100
        self.food = 100
        self.water = 100

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            self.x = new_x
            self.y = new_y

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Resource:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

    def draw(self):
        if self.type == 'food':
            color = GREEN
        elif self.type == 'water':
            color = BLUE
        else:  # health pack
            color = WHITE
        pygame.draw.rect(screen, color, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Hazard:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True  # New attribute to track if the hazard is still active

    def move(self):
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        new_x = (self.x + dx) % GRID_WIDTH
        new_y = (self.y + dy) % GRID_HEIGHT
        self.x, self.y = new_x, new_y

    def draw(self):
        if self.active:
            pygame.draw.rect(screen, PURPLE, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class TreeBranch:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fall_timer = random.randint(3, 8)  # Random time before falling

    def update(self, dt):
        self.fall_timer -= dt
        if self.fall_timer <= 0:
            self.y += 1
        return self.y < GRID_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, BROWN, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Game:
    def __init__(self):
        self.player = Player()
        self.resources = []
        self.hazards = []
        self.branches = []
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.spawn_timer = 0
        self.spawn_interval = 60  # Spawn a new resource every 60 frames (about 1 second at 60 FPS)
        self.stat_timer = 0
        self.hazard_move_timer = 0
        self.branch_spawn_timer = 0

    def spawn_resource(self):
        if len(self.resources) < 10 and self.spawn_timer <= 0:
            resource_type = random.choices(['food', 'water', 'health'], weights=[0.45, 0.45, 0.1])[0]
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            self.resources.append(Resource(x, y, resource_type))
            self.spawn_timer = self.spawn_interval
        else:
            self.spawn_timer -= 1

    def spawn_hazard(self):
        if len(self.hazards) < 5:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            self.hazards.append(Hazard(x, y))

    def spawn_branch(self):
        if len(self.branches) < 3:
            x = random.randint(0, GRID_WIDTH - 1)
            self.branches.append(TreeBranch(x, 0))

    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

    def draw_stats(self):
        health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
        food_text = self.font.render(f"Food: {self.player.food}", True, WHITE)
        water_text = self.font.render(f"Water: {self.player.water}", True, WHITE)
        screen.blit(health_text, (10, 10))
        screen.blit(food_text, (10, 50))
        screen.blit(water_text, (10, 90))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # Get time since last frame in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move(1, 0)
                    elif event.key == pygame.K_UP:
                        self.player.move(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.player.move(0, 1)

            self.spawn_resource()
            if random.random() < 0.01:  # 1% chance each frame to spawn a new hazard
                self.spawn_hazard()

            self.branch_spawn_timer += dt
            if self.branch_spawn_timer >= 2.0:  # Spawn a new branch every 2 seconds
                self.spawn_branch()
                self.branch_spawn_timer = 0

            # Check for collisions with resources
            for resource in self.resources[:]:
                if self.player.x == resource.x and self.player.y == resource.y:
                    if resource.type == 'food':
                        self.player.food = min(100, self.player.food + 20)
                    elif resource.type == 'water':
                        self.player.water = min(100, self.player.water + 20)
                    else:  # health pack
                        self.player.health = min(100, self.player.health + 30)
                    self.resources.remove(resource)

            # Check for collisions with hazards
            for hazard in self.hazards[:]:
                if self.player.x == hazard.x and self.player.y == hazard.y and hazard.active:
                    self.player.health -= 10  # Hazards now deal 10 damage on contact
                    hazard.active = False  # Deactivate the hazard
                    self.hazards.remove(hazard)  # Remove the hazard from the list

            # Update and check for collisions with branches
            for branch in self.branches[:]:
                if not branch.update(dt):
                    self.branches.remove(branch)
                elif self.player.x == branch.x and self.player.y == branch.y:
                    self.player.health -= 20  # Branches now deal 20 damage on contact
                    self.branches.remove(branch)

            # Move hazards
            self.hazard_move_timer += dt
            if self.hazard_move_timer >= 1.0:  # Move hazards every second
                for hazard in self.hazards:
                    if hazard.active:
                        hazard.move()
                self.hazard_move_timer = 0

            # Decrease stats over time
            self.stat_timer += dt
            if self.stat_timer >= 1.0:  # Every second
                self.player.food = max(0, self.player.food - 1)
                self.player.water = max(0, self.player.water - 1)
                if self.player.food == 0 or self.player.water == 0:
                    self.player.health = max(0, self.player.health - 1)
                self.stat_timer = 0  # Reset the timer

            # Game over condition
            if self.player.health <= 0:
                running = False

            screen.fill(BLACK)
            self.draw_grid()
            self.player.draw()
            for resource in self.resources:
                resource.draw()
            for hazard in self.hazards:
                if hazard.active:
                    hazard.draw()
            for branch in self.branches:
                branch.draw()
            self.draw_stats()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()