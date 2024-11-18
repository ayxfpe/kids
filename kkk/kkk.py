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
    def __init__(self, x, y, color, is_enemy=False):
        self.x = x
        self.y = y
        self.color = color
        self.angle = 0  # Add this line
        self.radius = 20
        self.speed = 8 if not is_enemy else 7  # Increased enemy speed
        self.health = 100
        self.ammo = 30
        self.is_enemy = is_enemy

    def move(self, forward=True):
        dx = math.cos(math.radians(self.angle)) * (self.speed if forward else -self.speed)
        dy = -math.sin(math.radians(self.angle)) * (self.speed if forward else -self.speed)
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 < new_x < WIDTH and 0 < new_y < HEIGHT:
            self.x = new_x
            self.y = new_y

    def rotate(self, angle):
        self.angle += angle
        self.angle %= 360

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        end_x = self.x + 30 * math.cos(math.radians(self.angle))
        end_y = self.y - 30 * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, self.color, (self.x, self.y), (end_x, end_y), 5)

    def shoot(self):
        dx = math.cos(math.radians(self.angle))
        dy = -math.sin(math.radians(self.angle))
        return Bullet(self.x, self.y, dx, dy, 'enemy' if self.is_enemy else 'player')

    # Add a new method for direct movement:
    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist != 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        self.angle = math.degrees(math.atan2(-dy, dx))

# Bullet class
class Bullet:
    def __init__(self, x, y, dx, dy, owner):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = 15
        self.radius = 8
        self.owner = owner  # 'player' or 'enemy'

    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self):
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius)

# Add this new class for AmmoPack
class AmmoPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.color = (255, 255, 0)  # Yellow color for ammo packs

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# Game class
class Game:
    def __init__(self):
        self.player = Player(100, HEIGHT // 2, BLUE)
        self.spawn_enemy()
        self.bullets = []
        self.ammo_packs = []  # New list to store ammo packs
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.enemy_move_timer = 0
        self.enemy_move_interval = 0.1
        self.enemy_shoot_timer = 0
        self.enemy_shoot_interval = 2.0
        self.game_over = False
        self.player_wins = False
        self.win_message_timer = 0

    def spawn_enemy(self):
        self.enemy = Player(WIDTH - 100, HEIGHT // 2, RED, is_enemy=True)
        self.enemy_shoot_timer = 0

    def spawn_ammo_pack(self):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        self.ammo_packs.append(AmmoPack(x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and self.player.ammo > 0:
                self.bullets.append(self.player.shoot())
                self.player.ammo -= 1
                if self.player.ammo == 0:
                    self.spawn_ammo_pack()  # Spawn an ammo pack when player runs out of ammo
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.rotate(5)  # Rotate clockwise
        if keys[pygame.K_RIGHT]:
            self.player.rotate(-5)  # Rotate counterclockwise
        if keys[pygame.K_UP]:
            self.player.move(forward=True)
        if keys[pygame.K_DOWN]:
            self.player.move(forward=False)
        return True

    def update(self):
        if self.game_over:
            return

        # Enemy movement
        self.enemy_move_timer += self.clock.get_time() / 1000  # Convert to seconds
        if self.enemy_move_timer >= self.enemy_move_interval:
            self.move_enemy()
            self.enemy_move_timer = 0

        # Enemy shooting
        self.enemy_shoot_timer += self.clock.get_time() / 1000
        if self.enemy_shoot_timer >= self.enemy_shoot_interval:
            self.enemy_shoot()
            self.enemy_shoot_timer = 0

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
                    self.player_wins = True
                    self.win_message_timer = 2

        # Check for ammo pack collection
        for ammo_pack in self.ammo_packs[:]:
            if math.hypot(ammo_pack.x - self.player.x, ammo_pack.y - self.player.y) < self.player.radius + ammo_pack.radius:
                self.player.ammo += 10  # Add 10 ammo when collected
                self.ammo_packs.remove(ammo_pack)

        if self.player_wins:
            self.win_message_timer -= self.clock.get_time() / 1000
            if self.win_message_timer <= 0:
                self.player_wins = False
                self.spawn_enemy()

    def enemy_shoot(self):
        if not self.player_wins:
            dx = self.player.x - self.enemy.x
            dy = self.player.y - self.enemy.y
            dist = math.sqrt(dx*dx + dy*dy)
            self.bullets.append(Bullet(self.enemy.x, self.enemy.y, dx/dist, dy/dist, 'enemy'))

    def move_enemy(self):
        self.enemy.move_towards(self.player.x, self.player.y)

    def draw(self):
        screen.fill(WHITE)
        self.player.draw()
        if not self.player_wins:
            self.enemy.draw()
        for bullet in self.bullets:
            bullet.draw()
        for ammo_pack in self.ammo_packs:
            ammo_pack.draw()
        
        player_health = self.font.render(f"Health: {self.player.health}", True, BLUE)
        enemy_health = self.font.render(f"Enemy Health: {self.enemy.health}", True, RED)
        ammo = self.font.render(f"Ammo: {self.player.ammo}", True, BLACK)
        screen.blit(player_health, (10, 10))
        screen.blit(enemy_health, (WIDTH - 200, 10))
        screen.blit(ammo, (10, 50))

        if self.game_over:
            game_over = self.font.render("Game Over! You lose!", True, BLACK)
            screen.blit(game_over, (WIDTH//2 - 100, HEIGHT//2))
        elif self.player_wins:
            win_text = self.font.render("You win! New enemy incoming...", True, BLACK)
            screen.blit(win_text, (WIDTH//2 - 150, HEIGHT//2))

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
