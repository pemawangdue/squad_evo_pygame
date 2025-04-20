import pygame
import sys
import os
import random

# Initialize game
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jetpack Chicken War")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 28)

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
difficulty_settings = {
    "Easy": {"enemy_speed": 2, "shoot_frequency": 60},
    "Medium": {"enemy_speed": 4, "shoot_frequency": 30},
    "Hard": {"enemy_speed": 6, "shoot_frequency": 10},
}

enemy_dizzy_sound = pygame.mixer.Sound(os.path.join("../assets/sounds", "dizzy-sound.mp3"))
player_hit_sound = pygame.mixer.Sound(os.path.join("../assets/sounds", "pain.wav"))
player_die_sound = pygame.mixer.Sound(os.path.join("../assets/sounds", "die.wav"))


# Load image
def load_image(name, width, height):
    img = pygame.image.load(os.path.join("../assets/images", name)).convert_alpha()
    return pygame.transform.scale(img, (width, height))


# Load assets
player_img = load_image("vinay-1.png", 60, 100)
chicken_img = load_image("chicken.png", 40, 30)
star_img = load_image("dizzy.png", 40, 40)  # Star image for fainting
background_img = load_image("background.png", WIDTH, HEIGHT)
heart_icon = load_image("heart.png", 30, 30)

player_frames = [
    load_image("vinay-1.png", 60, 100),
    load_image("vinay-2.png", 60, 100),
    load_image("vinay-3.png", 60, 100),
    load_image("vinay-4.png", 60, 100)
]

mosquito_frames = [
    [load_image("pema-1.png", 70, 50), load_image("pema-2.png", 70, 50)],
    [load_image("praful-1.png", 70, 50), load_image("praful-2.png", 70, 50)],
    [load_image("shreya-1.png", 70, 50), load_image("shreya-2.png", 70, 50)],
    [load_image("dheeraj-1.png", 70, 50), load_image("dheeraj-2.png", 70, 50)],
    [load_image("janhavi-1.png", 70, 50), load_image("janhavi-2.png", 70, 50)],
]


def play_music(file, loop=True):
    pygame.mixer.music.load(os.path.join("../assets/sounds", file))
    pygame.mixer.music.play(-1 if loop else 0)


def stop_music():
    pygame.mixer.music.stop()


# Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = player_frames
        self.current_frame = 0
        self.animation_timer = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(WIDTH - 100, HEIGHT // 2))
        self.speed = 5
        self.health = 5

        # Shooting cooldown
        self.shoot_cooldown = 300
        self.last_shot_time = pygame.time.get_ticks()

    def update(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] and self.rect.left > WIDTH // 2:  # Keep on right side
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

        # Animate if moving
        self.animation_timer += 1
        if self.animation_timer >= 8:  # adjust speed
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def can_shoot(self):
        now = pygame.time.get_ticks()
        return now - self.last_shot_time >= self.shoot_cooldown

    def shoot(self):
        self.last_shot_time = pygame.time.get_ticks()
        return Chicken(self.rect.centerx - 30, self.rect.centery)


class Chicken(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_image = chicken_img
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        # Projectile motion variables
        self.vx = -12
        self.vy = -6
        self.gravity = 0.5

        # Rotation
        self.angle = 0  # degrees

    def update(self):
        # Physics: projectile motion
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += self.gravity

        # Rotate chicken as it moves
        self.angle = (self.angle + 10) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)

        # Update rect to match new image size, and keep center
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)

        # Remove if off screen
        if self.rect.right < 0 or self.rect.top > HEIGHT:
            self.kill()


class Mosquito(pygame.sprite.Sprite):
    def __init__(self, frames, y_pos):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.animation_timer = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(50, y_pos))
        self.health = 2  # now 2 hits to die
        self.fainted = False
        self.speed = 4

        # Movement attributes
        self.dy = random.choice([-1, 1]) * random.randint(1, 2)
        self.dx = random.choice([-1, 1]) * random.randint(0, 1)
        self.move_timer = 0
        self.change_direction_interval = random.randint(30, 90)  # frames

        # Star blink
        self.star_timer = 0
        self.show_star = True

    def update(self):
        # Animate
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

        # Move (slower if fainted)
        speed_multiplier = 0.4 if self.fainted else 1
        actual_speed = self.speed * speed_multiplier
        self.rect.y += int(self.dy * actual_speed)
        self.rect.x += int(self.dx * actual_speed)

        # Bounce
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1
        if self.rect.left < 10 or self.rect.right > WIDTH // 2:
            self.dx *= -1

        # Change direction randomly
        self.move_timer += 1
        if self.move_timer > self.change_direction_interval:
            self.dy = random.choice([-1, 1]) * random.randint(1, 2)
            self.dx = random.choice([-1, 0, 1])
            self.move_timer = 0
            self.change_direction_interval = random.randint(30, 90)

        # Blink star if fainted
        if self.fainted:
            self.star_timer += 1
            if self.star_timer >= 30:  # blink interval
                self.star_timer = 0
                self.show_star = not self.show_star

    def shoot(self, player_rect):
        return EnemyBullet(self.rect.right, self.rect.centery, player_rect)

    def get_hit(self):
        if self.fainted:
            self.kill()  # Die on second hit
        else:
            self.fainted = True
            enemy_dizzy_sound.play()


class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_rect):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6

        # Calculate direction toward player
        dx = target_rect.centerx - x
        dy = target_rect.centery - y
        distance = max((dx ** 2 + dy ** 2) ** 0.5, 1)  # prevent division by zero
        speed = 5
        self.velocity = (dx / distance * speed, dy / distance * speed)

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if self.rect.left > WIDTH:
            self.kill()


# Text draw helper
def draw_text(text, size, color, x, y, center=True):
    font_obj = pygame.font.SysFont('Arial', size)
    text_surf = font_obj.render(text, True, color)
    text_rect = text_surf.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surf, text_rect)


# Game loop
def main():
    game_state = MENU
    score = 0
    start_time = 0
    result = ""

    player = Player()
    player_group = pygame.sprite.Group(player)
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    selected_difficulty = None  # Player's selection from the menu
    shoot_timer = 0
    shoot_frequency = 60
    previous_state = None

    while True:
        screen.blit(background_img, (0, 0))
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == GAME_OVER and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return main()

        if game_state == MENU:
            draw_text("Jetpack Chicken War", 48, BLACK, WIDTH // 2, HEIGHT // 4)
            draw_text("Select Difficulty:", 36, BLACK, WIDTH // 2, HEIGHT // 2 - 60)

            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()

            # Define buttons
            buttons = [("Easy", WIDTH // 2 - 150), ("Medium", WIDTH // 2), ("Hard", WIDTH // 2 + 150)]

            for text, x in buttons:
                rect = pygame.Rect(x - 60, HEIGHT // 2, 120, 40)
                color = (100, 200, 100) if text == selected_difficulty else (200, 200, 200)
                pygame.draw.rect(screen, color, rect)
                draw_text(text, 24, BLACK, x, HEIGHT // 2 + 20)

                if rect.collidepoint(mouse) and click[0]:
                    selected_difficulty = text

            # Start button only after difficulty selected
            if selected_difficulty:
                start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)
                pygame.draw.rect(screen, (0, 150, 250), start_rect)
                draw_text("Start Game", 28, WHITE, WIDTH // 2, HEIGHT // 2 + 125)

                if start_rect.collidepoint(mouse) and click[0]:
                    enemy_speed = difficulty_settings[selected_difficulty]["enemy_speed"]
                    shoot_frequency = difficulty_settings[selected_difficulty]["shoot_frequency"]
                    for i, frames in enumerate(mosquito_frames):
                        m = Mosquito(frames, 50 + i * 100)
                        m.speed = enemy_speed  # add speed to the mosquito object
                        enemies.add(m)

                    game_state = PLAYING
                    start_time = pygame.time.get_ticks()

        elif game_state == PLAYING:

            player_group.update(keys)
            bullets.update()
            enemy_bullets.update()
            enemies.update()

            # Shooting
            if keys[pygame.K_SPACE] and player.can_shoot():
                bullets.add(player.shoot())

            shoot_timer += 1
            if shoot_timer >= shoot_frequency:
                shoot_timer = 0
                if enemies.sprites():
                    shooter = random.choice(enemies.sprites())
                    enemy_bullets.add(shooter.shoot(player.rect))

            # Bullet collisions
            for bullet in bullets:
                hit = pygame.sprite.spritecollideany(bullet, enemies)
                if hit:
                    bullet.kill()
                    hit.get_hit()

            # Enemy bullets hit player
            if pygame.sprite.spritecollideany(player, enemy_bullets):
                player.health -= 1
                for b in enemy_bullets:
                    if player.rect.colliderect(b.rect):
                        b.kill()
                if player.health <= 0:
                    player_die_sound.play()
                    game_state = GAME_OVER
                    result = "You Lose!"
                else:
                    player_hit_sound.play()

            # Win condition
            if len(enemies) == 0:
                game_state = GAME_OVER
                result = "You Win!"

            score = (pygame.time.get_ticks() - start_time) // 1000

            # Draw everything
            player_group.draw(screen)
            bullets.draw(screen)
            enemy_bullets.draw(screen)
            enemies.draw(screen)

            # Draw fainting star if necessary
            for enemy in enemies:
                if enemy.fainted and enemy.show_star:
                    screen.blit(star_img, (enemy.rect.centerx - 10, enemy.rect.top - 20))

            for i in range(player.health):
                screen.blit(heart_icon, (10 + i * 35, 10))
            draw_text(f"Score: {score}", 24, BLACK, 10, 40, center=False)

        elif game_state == GAME_OVER:
            draw_text(result, 50, RED, WIDTH // 2, HEIGHT // 3)
            draw_text(f"Final Score: {score}", 30, BLACK, WIDTH // 2, HEIGHT // 2)
            draw_text("Press R to Restart", 25, BLACK, WIDTH // 2, HEIGHT // 2 + 50)

        if game_state != previous_state:
            if game_state == MENU:
                play_music("background.mp3")
            elif game_state == GAME_OVER:
                stop_music()
                play_music("game-over.mp3", False)
            previous_state = game_state

        pygame.display.flip()
        clock.tick(60)


# Run it
if __name__ == "__main__":
    main()
