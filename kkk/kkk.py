import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CS Battle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BRIGHT_YELLOW = (255, 255, 0)  # Bright yellow for bullets

# Player class
class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 20
        self.speed = 5
        self.health = 100
        self.ammo = 30

    def move(self, dx, dy):
        self.x = max(self.radius, min(WIDTH - self.radius, self.x + dx * self.speed))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y + dy * self.speed))

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Bullet class
class Bullet:
    def __init__(self, x, y, dx, dy, owner):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = 10
        self.radius = 8
        self.owner = owner  # 'player' or 'enemy'

    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)

# Game class
class Game:
    def __init__(self):
        self.player = Player(100, HEIGHT // 2, BLUE)
        self.enemy = Player(WIDTH - 100, HEIGHT // 2, RED)
        self.bullets = []
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and self.player.ammo > 0:
                mx, my = pygame.mouse.get_pos()
                dx = mx - self.player.x
                dy = my - self.player.y
                dist = math.sqrt(dx*dx + dy*dy)
                self.bullets.append(Bullet(self.player.x, self.player.y, dx/dist, dy/dist, 'player'))
                self.player.ammo -= 1
        return True

    def update(self):
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        self.player.move(dx, dy)

        # Simple AI for enemy
        if random.random() < 0.02:  # 2% chance to shoot each frame
            dx = self.player.x - self.enemy.x
            dy = self.player.y - self.enemy.y
            dist = math.sqrt(dx*dx + dy*dy)
            self.bullets.append(Bullet(self.enemy.x, self.enemy.y, dx/dist, dy/dist, 'enemy'))

        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                self.bullets.remove(bullet)
            elif bullet.owner == 'enemy' and math.hypot(bullet.x - self.player.x, bullet.y - self.player.y) < self.player.radius:
                self.player.health -= 10
                self.bullets.remove(bullet)
            elif bullet.owner == 'player' and math.hypot(bullet.x - self.enemy.x, bullet.y - self.enemy.y) < self.enemy.radius:
                self.enemy.health -= 10
                self.bullets.remove(bullet)

    def draw(self):
        screen.fill(WHITE)
        self.player.draw()
        self.enemy.draw()
        for bullet in self.bullets:
            bullet.draw()
        
        player_health = self.font.render(f"Health: {self.player.health}", True, BLUE)
        enemy_health = self.font.render(f"Enemy Health: {self.enemy.health}", True, RED)
        ammo = self.font.render(f"Ammo: {self.player.ammo}", True, BLACK)
        screen.blit(player_health, (10, 10))
        screen.blit(enemy_health, (WIDTH - 200, 10))
        screen.blit(ammo, (10, 50))

        if self.player.health <= 0 or self.enemy.health <= 0:
            winner = "Enemy" if self.player.health <= 0 else "Player"
            game_over = self.font.render(f"Game Over! {winner} wins!", True, BLACK)
            screen.blit(game_over, (WIDTH//2 - 100, HEIGHT//2))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
