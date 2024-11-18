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
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)

class Player:
    def __init__(self):
        self.x = GRID_WIDTH // 2
        self.y = GRID_HEIGHT - 2
        self.health = 100
        self.food = 100
        self.water = 100
        self.ammo = 0
        self.last_dx = 0
        self.last_dy = 0

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            self.x = new_x
            self.y = new_y
            if dx != 0 or dy != 0:
                self.last_dx = dx
                self.last_dy = dy

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
        self.active = True

    def move(self, player_x, player_y):
        if not self.active:
            return

        # Calculate direction towards the player
        dx = player_x - self.x
        dy = player_y - self.y

        # Normalize the direction
        length = max(abs(dx), abs(dy), 1)
        dx = dx / length
        dy = dy / length

        # Move towards the player
        new_x = self.x + (1 if dx > 0 else -1 if dx < 0 else 0)
        new_y = self.y + (1 if dy > 0 else -1 if dy < 0 else 0)

        # Ensure the hazard stays within the grid
        self.x = max(0, min(GRID_WIDTH - 1, new_x))
        self.y = max(0, min(GRID_HEIGHT - 1, new_y))

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

class Gun:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.rect(screen, DARK_GRAY, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def update(self):
        self.x += self.dx * 2  # Move 2 blocks per update
        self.y += self.dy * 2
        return 0 <= self.x < GRID_WIDTH and 0 <= self.y < GRID_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

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
        self.max_resources = 5  # Set the maximum number of resources
        self.guns = []
        self.bullets = []
        self.gun_spawn_timer = 0
        self.gun_spawn_interval = 300  # Spawn a gun every 5 seconds (300 frames)
        self.shoot_timer = 0

    def spawn_resource(self):
        if len(self.resources) < self.max_resources and self.spawn_timer <= 0:
            resource_type = random.choices(['food', 'water', 'health'], weights=[0.4, 0.4, 0.2])[0]
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

    def spawn_gun(self):
        if len(self.guns) < 1 and self.gun_spawn_timer <= 0:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            self.guns.append(Gun(x, y))
            self.gun_spawn_timer = self.gun_spawn_interval
        else:
            self.gun_spawn_timer -= 1

    def draw_grid(self):
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

    def draw_stats(self):
        health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
        food_text = self.font.render(f"Food: {self.player.food}", True, WHITE)
        water_text = self.font.render(f"Water: {self.player.water}", True, WHITE)
        ammo_text = self.font.render(f"Ammo: {self.player.ammo}", True, WHITE)
        screen.blit(health_text, (10, 10))
        screen.blit(food_text, (10, 50))
        screen.blit(water_text, (10, 90))
        screen.blit(ammo_text, (10, 130))

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
                    elif event.key == pygame.K_SPACE and self.player.ammo > 0:
                        if self.shoot_timer <= 0 and (self.player.last_dx != 0 or self.player.last_dy != 0):
                            self.bullets.append(Bullet(self.player.x, self.player.y, 
                                                    self.player.last_dx, self.player.last_dy))
                            self.player.ammo -= 1
                            self.shoot_timer = 30  # Half second cooldown between shots

            self.spawn_resource()
            self.spawn_gun()
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
                        hazard.move(self.player.x, self.player.y)
                self.hazard_move_timer = 0

            # Decrease stats over time
            self.stat_timer += dt
            if self.stat_timer >= 1.0:  # Every second
                self.player.food = max(0, self.player.food - 1)
                self.player.water = max(0, self.player.water - 1)
                if self.player.food == 0 or self.player.water == 0:
                    self.player.health = max(0, self.player.health - 1)
                self.stat_timer = 0  # Reset the timer

            # Check for collisions with guns
            for gun in self.guns[:]:
                if self.player.x == gun.x and self.player.y == gun.y:
                    self.player.ammo = min(10, self.player.ammo + 10)  # Give 10 ammo, max 10
                    self.guns.remove(gun)

            # Update bullets and check for collisions
            for bullet in self.bullets[:]:
                if not bullet.update():
                    self.bullets.remove(bullet)
                else:
                    for hazard in self.hazards[:]:
                        if int(bullet.x) == hazard.x and int(bullet.y) == hazard.y and hazard.active:
                            if random.random() < 0.8:  # 80% chance to hit
                                self.hazards.remove(hazard)
                            self.bullets.remove(bullet)
                            break

            if self.shoot_timer > 0:
                self.shoot_timer -= 1

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
            for gun in self.guns:
                gun.draw()
            for bullet in self.bullets:
                bullet.draw()
            self.draw_stats()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()