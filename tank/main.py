import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Tank class
class Tank:
    def __init__(self, x, y, color, is_enemy=False):
        self.x = x
        self.y = y
        self.color = color
        self.angle = 0
        self.speed = 3 if not is_enemy else 2
        self.rotation_speed = 3
        self.health = 100
        self.radius = 20
        self.is_enemy = is_enemy

    def move(self, forward=True):
        dx = math.cos(math.radians(self.angle)) * (self.speed if forward else -self.speed)
        dy = -math.sin(math.radians(self.angle)) * (self.speed if forward else -self.speed)
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 < new_x < WIDTH and 0 < new_y < HEIGHT:
            self.x = new_x
            self.y = new_y

    def rotate(self, clockwise=True):
        self.angle += self.rotation_speed if clockwise else -self.rotation_speed
        self.angle %= 360

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        end_x = self.x + 30 * math.cos(math.radians(self.angle))
        end_y = self.y - 30 * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 5)

    def shoot(self):
        bullet_x = self.x + 35 * math.cos(math.radians(self.angle))
        bullet_y = self.y - 35 * math.sin(math.radians(self.angle))
        return Bullet(bullet_x, bullet_y, self.angle, 'enemy' if self.is_enemy else 'player')

# Bullet class
class Bullet:
    def __init__(self, x, y, angle, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 7
        self.owner = owner

    def move(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y -= math.sin(math.radians(self.angle)) * self.speed

    def draw(self):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 5)

# Game class
class Game:
    def __init__(self):
        self.player = Tank(100, HEIGHT // 2, BLUE)
        self.enemy = Tank(WIDTH - 100, HEIGHT // 2, RED, is_enemy=True)
        self.bullets = []
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.enemy_shoot_timer = 0
        self.enemy_shoot_interval = 2.0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.bullets.append(self.player.shoot())
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.rotate(clockwise=False)
        if keys[pygame.K_RIGHT]:
            self.player.rotate(clockwise=True)
        if keys[pygame.K_UP]:
            self.player.move(forward=True)
        if keys[pygame.K_DOWN]:
            self.player.move(forward=False)
        
        return True

    def update(self):
        if self.game_over:
            return

        # Enemy behavior
        self.enemy_shoot_timer += self.clock.get_time() / 1000
        if self.enemy_shoot_timer >= self.enemy_shoot_interval:
            self.enemy_shoot()
            self.enemy_shoot_timer = 0

        self.enemy_tank_behavior()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                self.bullets.remove(bullet)
            elif bullet.owner == 'enemy' and math.hypot(bullet.x - self.player.x, bullet.y - self.player.y) < self.player.radius:
                self.player.health -= 10
                self.bullets.remove(bullet)
                if self.player.health <= 0:
                    self.game_over = True
            elif bullet.owner == 'player' and math.hypot(bullet.x - self.enemy.x, bullet.y - self.enemy.y) < self.enemy.radius:
                self.enemy.health -= 10
                self.bullets.remove(bullet)
                if self.enemy.health <= 0:
                    self.game_over = True

    def enemy_tank_behavior(self):
        # Calculate angle to player
        dx = self.player.x - self.enemy.x
        dy = self.player.y - self.enemy.y
        angle_to_player = math.degrees(math.atan2(-dy, dx))
        
        # Rotate towards the player
        angle_diff = (angle_to_player - self.enemy.angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
        if angle_diff > 0:
            self.enemy.rotate(clockwise=True)
        elif angle_diff < 0:
            self.enemy.rotate(clockwise=False)

        # Move towards the player if far away
        distance = math.hypot(dx, dy)
        if distance > 200:
            self.enemy.move(forward=True)

    def enemy_shoot(self):
        self.bullets.append(self.enemy.shoot())

    def draw(self):
        screen.fill(WHITE)
        self.player.draw()
        self.enemy.draw()
        for bullet in self.bullets:
            bullet.draw()
        
        player_health = self.font.render(f"Player Health: {self.player.health}", True, BLUE)
        enemy_health = self.font.render(f"Enemy Health: {self.enemy.health}", True, RED)
        screen.blit(player_health, (10, 10))
        screen.blit(enemy_health, (WIDTH - 220, 10))

        if self.game_over:
            winner = "Player" if self.enemy.health <= 0 else "Enemy"
            game_over_text = self.font.render(f"Game Over! {winner} wins!", True, GREEN)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))

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
