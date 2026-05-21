import pygame
import random
import math
import time

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival FINAL")

clock = pygame.time.Clock()

# COLORS
BG = (18, 18, 25)

PLAYER_COLOR = (0, 255, 255)
ZOMBIE_NORMAL = (0, 180, 0)
ZOMBIE_FAST = (200, 200, 0)
ZOMBIE_TANK = (0, 80, 255)
BULLET_COLOR = (255, 60, 60)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

font = pygame.font.SysFont("consolas", 22)

# SHAKE
shake = 0

def screen_shake():
    global shake
    if shake > 0:
        shake -= 1
    return (random.randint(-shake, shake), random.randint(-shake, shake))

# TIMER START
start_time = time.time()

# PLAYER
player = pygame.Rect(500, 350, 40, 40)
speed = 5

up = down = left = right = False
direction = "up"

# GAME
bullets = []
zombies = []

score = 0
health = 5

# LEVEL / WAVE
wave = 1
kills = 0
wave_target = 5

# ---------------- ZOMBIE ----------------
def spawn_zombie():
    x, y = random.randint(50, 950), -40

    if wave < 3:
        zombies.append([pygame.Rect(x, y, 35, 35), 2, 1, ZOMBIE_NORMAL, "normal"])
    elif wave < 6:
        t = random.choice(["normal", "fast"])
        if t == "fast":
            zombies.append([pygame.Rect(x, y, 25, 25), 3.5, 1, ZOMBIE_FAST, "fast"])
        else:
            zombies.append([pygame.Rect(x, y, 35, 35), 2.2, 1, ZOMBIE_NORMAL, "normal"])
    else:
        t = random.choice(["normal", "fast", "tank"])
        if t == "tank":
            zombies.append([pygame.Rect(x, y, 60, 60), 1.2, 3, ZOMBIE_TANK, "tank"])
        elif t == "fast":
            zombies.append([pygame.Rect(x, y, 25, 25), 4, 1, ZOMBIE_FAST, "fast"])
        else:
            zombies.append([pygame.Rect(x, y, 35, 35), 2.5, 1, ZOMBIE_NORMAL, "normal"])

# ---------------- SHOOT ----------------
def shoot():
    b = pygame.Rect(player.centerx, player.centery, 6, 6)

    if direction == "up":
        bullets.append([b, 0, -12])
    elif direction == "down":
        bullets.append([b, 0, 12])
    elif direction == "left":
        bullets.append([b, -12, 0])
    elif direction == "right":
        bullets.append([b, 12, 0])

# ---------------- LOOP ----------------
running = True
spawn_timer = 0

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                shoot()

            if event.key == pygame.K_w:
                up = True
                direction = "up"
            if event.key == pygame.K_s:
                down = True
                direction = "down"
            if event.key == pygame.K_a:
                left = True
                direction = "left"
            if event.key == pygame.K_d:
                right = True
                direction = "right"

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w: up = False
            if event.key == pygame.K_s: down = False
            if event.key == pygame.K_a: left = False
            if event.key == pygame.K_d: right = False

    # MOVE PLAYER
    dx = dy = 0
    if up: dy = -speed
    if down: dy = speed
    if left: dx = -speed
    if right: dx = speed

    player.x += dx
    player.y += dy

    # BULLETS
    for b in bullets[:]:
        b[0].x += b[1]
        b[0].y += b[2]

        if not screen.get_rect().colliderect(b[0]):
            bullets.remove(b)

    # SPAWN
    spawn_timer += 1
    if spawn_timer > max(20, 60 - wave * 3):
        spawn_zombie()
        spawn_timer = 0

    # ZOMBIES
    for z in zombies[:]:
        r, spd, hp, col, typ = z

        dx = player.x - r.x
        dy = player.y - r.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))

        r.x += int(dx / dist * spd)
        r.y += int(dy / dist * spd)

        # PLAYER HIT
        if r.colliderect(player):
            zombies.remove(z)
            health -= 1

            if typ == "tank":
                shake = 12

        # BULLET HIT
        for b in bullets[:]:
            if r.colliderect(b[0]):
                z[2] -= 1
                bullets.remove(b)

                if z[2] <= 0:
                    zombies.remove(z)
                    score += 1
                    kills += 1

                    # 💥 BIG ZOMBIE SHAKE
                    if typ == "tank":
                        shake = 15
                    elif typ == "fast":
                        shake = 6
                break

    # WAVE SYSTEM
    if kills >= wave_target:
        wave += 1
        kills = 0
        wave_target += 3

    # TIMER
    elapsed = int(time.time() - start_time)

    # DRAW
    offset = screen_shake()

    screen.fill(BG)

    # PLAYER
    pygame.draw.rect(screen, PLAYER_COLOR, player.move(offset), border_radius=8)

    # ZOMBIES
    for z in zombies:
        pygame.draw.rect(screen, z[3], z[0].move(offset), border_radius=6)

    # BULLETS
    for b in bullets:
        pygame.draw.rect(screen, BULLET_COLOR, b[0].move(offset))

    # UI
    screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 20))
    screen.blit(font.render(f"Health: {health}", True, WHITE), (20, 45))
    screen.blit(font.render(f"Wave: {wave}", True, WHITE), (20, 70))
    screen.blit(font.render(f"Time: {elapsed}s", True, WHITE), (20, 95))

    # GAME OVER
    if health <= 0:
        screen.blit(font.render("GAME OVER", True, RED), (450, 350))
        pygame.display.flip()
        pygame.time.wait(2000)
        running = False

    pygame.display.flip()

pygame.quit()