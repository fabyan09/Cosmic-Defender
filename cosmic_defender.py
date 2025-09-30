import pygame
import random
import math
import sys
import json
import os
from datetime import datetime
from enum import Enum

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    VICTORY = 4
    LEADERBOARD = 5
    ENTER_NAME = 6

class PowerUpType(Enum):
    RAPID_FIRE = 1
    SHIELD = 2
    MULTI_SHOT = 3
    LASER = 4

class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.age = 0

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        return self.age < self.lifetime

    def draw(self, screen):
        alpha = max(0, 1 - self.age / self.lifetime)
        color = tuple(int(c * alpha) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)

class Bullet:
    def __init__(self, x, y, velocity, damage=1, color=YELLOW):
        self.x = x
        self.y = y
        self.vx, self.vy = velocity
        self.damage = damage
        self.color = color
        self.rect = pygame.Rect(x-2, y-2, 4, 8)

    def update(self, dt, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))
        return 0 <= self.x <= screen_width and 0 <= self.y <= screen_height

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)

class Enemy:
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.health = 1
        self.speed = 100
        self.size = 20
        self.color = RED
        self.shoot_timer = 0
        self.shoot_cooldown = 2.0
        self.points = 10

        if enemy_type == "tank":
            self.health = 3
            self.speed = 50
            self.size = 30
            self.color = (150, 0, 0)
            self.points = 25
        elif enemy_type == "fast":
            self.speed = 200
            self.size = 15
            self.color = (255, 100, 100)
            self.shoot_cooldown = 1.5
            self.points = 15
        elif enemy_type == "boss":
            self.health = 20
            self.speed = 30
            self.size = 50
            self.color = (100, 0, 100)
            self.shoot_cooldown = 0.5
            self.points = 100

        self.rect = pygame.Rect(x-self.size//2, y-self.size//2, self.size, self.size)

    def update(self, dt, player_x, player_y, screen_height=SCREEN_HEIGHT):
        if self.enemy_type == "boss":
            self.y += self.speed * dt * 0.5
            self.x += math.sin(self.y * 0.01) * 50 * dt
        else:
            angle = math.atan2(player_y - self.y, player_x - self.x)
            self.x += math.cos(angle) * self.speed * dt * 0.3
            self.y += self.speed * dt

        self.rect.center = (int(self.x), int(self.y))
        self.shoot_timer += dt

        return self.y < screen_height + 50

    def can_shoot(self):
        if self.shoot_timer >= self.shoot_cooldown:
            self.shoot_timer = 0
            return True
        return False

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def draw(self, screen):
        health_ratio = self.health / (3 if self.enemy_type == "tank" else 20 if self.enemy_type == "boss" else 1)
        current_color = tuple(int(c * health_ratio) for c in self.color)

        if self.enemy_type == "boss":
            pygame.draw.ellipse(screen, current_color, self.rect)
            pygame.draw.ellipse(screen, WHITE, self.rect, 3)
        else:
            pygame.draw.rect(screen, current_color, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 2)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.size = 15
        self.float_offset = 0
        self.rect = pygame.Rect(x-self.size//2, y-self.size//2, self.size*2, self.size*2)

        colors = {
            PowerUpType.RAPID_FIRE: ORANGE,
            PowerUpType.SHIELD: CYAN,
            PowerUpType.MULTI_SHOT: GREEN,
            PowerUpType.LASER: PURPLE
        }
        self.color = colors.get(power_type, WHITE)

    def update(self, dt, screen_height=SCREEN_HEIGHT):
        self.float_offset += dt * 3
        self.y += 50 * dt
        self.rect.center = (int(self.x), int(self.y + math.sin(self.float_offset) * 3))
        return self.y < screen_height + 20

    def draw(self, screen):
        y_pos = int(self.y + math.sin(self.float_offset) * 3)
        pygame.draw.circle(screen, self.color, (int(self.x), y_pos), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x), y_pos), self.size, 2)

class Player:
    def __init__(self, x, y, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 300
        self.size = 15
        self.health = 100
        self.max_health = 100
        self.shield = 0
        self.max_shield = 50
        self.rect = pygame.Rect(x-self.size, y-self.size, self.size*2, self.size*2)

        self.shoot_cooldown = 0.2
        self.shoot_timer = 0
        self.rapid_fire_timer = 0
        self.multi_shot_timer = 0
        self.laser_timer = 0

        self.power_up_duration = 5.0

    def update_screen_bounds(self, width, height):
        self.screen_width = width
        self.screen_height = height

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * dt

        self.x = max(self.size, min(self.screen_width - self.size, self.x))
        self.y = max(self.size, min(self.screen_height - self.size, self.y))

        self.rect.center = (int(self.x), int(self.y))
        self.shoot_timer += dt

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= dt
        if self.multi_shot_timer > 0:
            self.multi_shot_timer -= dt
        if self.laser_timer > 0:
            self.laser_timer -= dt

    def can_shoot(self):
        cooldown = 0.1 if self.rapid_fire_timer > 0 else self.shoot_cooldown
        if self.shoot_timer >= cooldown:
            self.shoot_timer = 0
            return True
        return False

    def get_bullets(self):
        bullets = []
        if self.laser_timer > 0:
            bullets.append(Bullet(self.x, self.y - self.size, (0, -800), damage=3, color=PURPLE))
        elif self.multi_shot_timer > 0:
            bullets.extend([
                Bullet(self.x, self.y - self.size, (0, -600)),
                Bullet(self.x - 15, self.y - self.size, (-100, -600)),
                Bullet(self.x + 15, self.y - self.size, (100, -600))
            ])
        else:
            bullets.append(Bullet(self.x, self.y - self.size, (0, -600)))
        return bullets

    def activate_power_up(self, power_type):
        if power_type == PowerUpType.RAPID_FIRE:
            self.rapid_fire_timer = self.power_up_duration
        elif power_type == PowerUpType.SHIELD:
            self.shield = min(self.max_shield, self.shield + 25)
        elif power_type == PowerUpType.MULTI_SHOT:
            self.multi_shot_timer = self.power_up_duration
        elif power_type == PowerUpType.LASER:
            self.laser_timer = self.power_up_duration

    def take_damage(self, damage):
        if self.shield > 0:
            shield_damage = min(self.shield, damage)
            self.shield -= shield_damage
            damage -= shield_damage

        self.health -= damage
        return self.health <= 0

    def draw(self, screen):
        if self.shield > 0:
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.size + 5, 2)

        color = GREEN
        if self.rapid_fire_timer > 0:
            color = ORANGE
        elif self.multi_shot_timer > 0:
            color = GREEN
        elif self.laser_timer > 0:
            color = PURPLE

        points = [
            (self.x, self.y - self.size),
            (self.x - self.size, self.y + self.size),
            (self.x + self.size, self.y + self.size)
        ]
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)

class CosmicDefender:
    def __init__(self):
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Cosmic Defender")
        self.clock = pygame.time.Clock()
        self.running = True

        # Current screen dimensions (updated when switching modes)
        self.current_width = SCREEN_WIDTH
        self.current_height = SCREEN_HEIGHT

        self.state = GameState.MENU
        self.player = Player(self.current_width // 2, self.current_height - 100, self.current_width, self.current_height)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.power_ups = []
        self.particles = []

        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_per_wave = 10
        self.spawn_timer = 0
        self.spawn_cooldown = 1.0

        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.stars = [(random.randint(0, self.current_width), random.randint(0, self.current_height)) for _ in range(100)]

        # Score system
        self.scores_file = "scores.json"
        self.player_name = ""
        self.name_input_active = False
        self.cursor_timer = 0

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.current_width, self.current_height = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            self.current_width, self.current_height = SCREEN_WIDTH, SCREEN_HEIGHT

        # Regenerate stars for new screen size
        self.stars = [(random.randint(0, self.current_width), random.randint(0, self.current_height)) for _ in range(100)]

        # Update player bounds
        if hasattr(self, 'player') and self.player:
            self.player.update_screen_bounds(self.current_width, self.current_height)

    def load_scores(self):
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_score(self, name, score, wave):
        scores = self.load_scores()
        new_score = {
            "name": name,
            "score": score,
            "wave": wave,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        scores.append(new_score)
        scores.sort(key=lambda x: x["score"], reverse=True)
        scores = scores[:10]  # Keep only top 10

        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")

    def get_top_scores(self):
        return self.load_scores()[:10]

    def spawn_enemy(self):
        x = random.randint(50, self.current_width - 50)
        y = -50

        rand = random.random()
        if self.wave >= 5 and rand < 0.1:
            enemy_type = "boss"
        elif rand < 0.2:
            enemy_type = "tank"
        elif rand < 0.4:
            enemy_type = "fast"
        else:
            enemy_type = "basic"

        self.enemies.append(Enemy(x, y, enemy_type))

    def spawn_power_up(self, x, y):
        if random.random() < 0.3:
            power_type = random.choice(list(PowerUpType))
            self.power_ups.append(PowerUp(x, y, power_type))

    def create_explosion(self, x, y, color=ORANGE, count=10):
        for _ in range(count):
            velocity = (random.uniform(-200, 200), random.uniform(-200, 200))
            self.particles.append(Particle(x, y, color, velocity, random.uniform(0.5, 1.5)))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE and self.fullscreen:
                    self.toggle_fullscreen()
                elif self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_l:  # L for Leaderboard
                        self.state = GameState.LEADERBOARD
                elif self.state == GameState.LEADERBOARD:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                elif self.state == GameState.ENTER_NAME:
                    if event.key == pygame.K_RETURN and len(self.player_name.strip()) > 0:
                        self.save_score(self.player_name.strip(), self.score, self.wave)
                        self.player_name = ""
                        self.name_input_active = False
                        self.state = GameState.LEADERBOARD
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.player_name = ""
                        self.name_input_active = False
                        self.state = GameState.MENU
                    elif len(self.player_name) < 20 and event.unicode.isprintable():
                        self.player_name += event.unicode
                elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                    if event.key == pygame.K_s:  # S to save score
                        self.player_name = ""
                        self.name_input_active = True
                        self.state = GameState.ENTER_NAME
                    elif event.key == pygame.K_r:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU

    def start_game(self):
        self.state = GameState.PLAYING
        self.player = Player(self.current_width // 2, self.current_height - 100, self.current_width, self.current_height)
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.power_ups.clear()
        self.particles.clear()
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.spawn_timer = 0

    def update_game(self, dt):
        self.player.update(dt)

        if self.player.can_shoot() and (pygame.key.get_pressed()[pygame.K_SPACE] or
                                       pygame.mouse.get_pressed()[0]):
            self.bullets.extend(self.player.get_bullets())

        self.bullets = [bullet for bullet in self.bullets if bullet.update(dt, self.current_width, self.current_height)]
        self.enemy_bullets = [bullet for bullet in self.enemy_bullets if bullet.update(dt, self.current_width, self.current_height)]

        for enemy in self.enemies[:]:
            if not enemy.update(dt, self.player.x, self.player.y, self.current_height):
                self.enemies.remove(enemy)
                continue

            if enemy.can_shoot():
                angle = math.atan2(self.player.y - enemy.y, self.player.x - enemy.x)
                velocity = (math.cos(angle) * 200, math.sin(angle) * 200)
                self.enemy_bullets.append(Bullet(enemy.x, enemy.y, velocity, color=RED))

        self.power_ups = [power_up for power_up in self.power_ups if power_up.update(dt, self.current_height)]
        self.particles = [particle for particle in self.particles if particle.update(dt)]

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if enemy.take_damage(bullet.damage):
                        self.score += enemy.points
                        self.create_explosion(enemy.x, enemy.y)
                        self.spawn_power_up(enemy.x, enemy.y)
                        self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    break

        for bullet in self.enemy_bullets[:]:
            if bullet.rect.colliderect(self.player.rect):
                if self.player.take_damage(bullet.damage):
                    self.state = GameState.GAME_OVER
                self.create_explosion(self.player.x, self.player.y, RED)
                self.enemy_bullets.remove(bullet)

        for power_up in self.power_ups[:]:
            if power_up.rect.colliderect(self.player.rect):
                self.player.activate_power_up(power_up.type)
                self.power_ups.remove(power_up)
                self.create_explosion(power_up.x, power_up.y, power_up.color, 5)

        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(10):
                    self.state = GameState.GAME_OVER
                self.create_explosion(self.player.x, self.player.y, RED)
                self.enemies.remove(enemy)

        self.spawn_timer += dt
        if (self.spawn_timer >= self.spawn_cooldown and
            self.enemies_spawned < self.enemies_per_wave and
            len(self.enemies) < 15):
            self.spawn_enemy()
            self.enemies_spawned += 1
            self.spawn_timer = 0

        if self.enemies_spawned >= self.enemies_per_wave and len(self.enemies) == 0:
            self.wave += 1
            self.enemies_spawned = 0
            self.enemies_per_wave += 2
            self.spawn_cooldown = max(0.3, self.spawn_cooldown - 0.05)

            if self.wave > 10:
                self.state = GameState.VICTORY

    def draw_stars(self):
        for star in self.stars:
            pygame.draw.circle(self.screen, WHITE, star, 1)

    def draw_ui(self):
        health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
        shield_text = self.font.render(f"Shield: {self.player.shield}", True, CYAN)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)

        self.screen.blit(health_text, (10, 10))
        self.screen.blit(shield_text, (10, 50))
        self.screen.blit(score_text, (self.current_width - 150, 10))
        self.screen.blit(wave_text, (self.current_width - 150, 50))

        health_bar_width = 200
        health_ratio = self.player.health / self.player.max_health
        health_color = GREEN if health_ratio > 0.5 else ORANGE if health_ratio > 0.25 else RED

        pygame.draw.rect(self.screen, RED, (10, 90, health_bar_width, 10))
        pygame.draw.rect(self.screen, health_color, (10, 90, health_bar_width * health_ratio, 10))

        if self.player.shield > 0:
            shield_ratio = self.player.shield / self.player.max_shield
            pygame.draw.rect(self.screen, CYAN, (10, 105, health_bar_width * shield_ratio, 5))

    def draw_menu(self):
        title = self.big_font.render("COSMIC DEFENDER", True, WHITE)
        subtitle = self.font.render("Press SPACE to start", True, WHITE)
        instructions = [
            "WASD or Arrow Keys: Move",
            "SPACE or Click: Shoot",
            "F11: Toggle Fullscreen",
            "L: View Leaderboard",
            "Collect power-ups to upgrade!",
            "Survive 10 waves to win!"
        ]

        title_rect = title.get_rect(center=(self.current_width//2, self.current_height//2 - 100))
        subtitle_rect = subtitle.get_rect(center=(self.current_width//2, self.current_height//2 - 50))

        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)

        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(self.current_width//2, self.current_height//2 + i * 30 + 50))
            self.screen.blit(text, text_rect)

    def draw_game_over(self):
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        wave_text = self.font.render(f"Wave Reached: {self.wave}", True, WHITE)
        restart_text = self.font.render("Press S to save score, R to restart or ESC for menu", True, WHITE)

        texts = [game_over_text, score_text, wave_text, restart_text]
        for i, text in enumerate(texts):
            text_rect = text.get_rect(center=(self.current_width//2, self.current_height//2 - 60 + i * 40))
            self.screen.blit(text, text_rect)

    def draw_victory(self):
        victory_text = self.big_font.render("VICTORY!", True, GREEN)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        congrats_text = self.font.render("You saved Earth from invasion!", True, WHITE)
        restart_text = self.font.render("Press S to save score, R to play again or ESC for menu", True, WHITE)

        texts = [victory_text, score_text, congrats_text, restart_text]
        for i, text in enumerate(texts):
            text_rect = text.get_rect(center=(self.current_width//2, self.current_height//2 - 60 + i * 40))
            self.screen.blit(text, text_rect)

    def draw_enter_name(self):
        title = self.big_font.render("SAVE YOUR SCORE", True, WHITE)
        instruction = self.font.render("Enter your name:", True, WHITE)

        # Cursor blinking effect
        show_cursor = (self.cursor_timer % 1.0) < 0.5
        name_display = self.player_name + ("|" if show_cursor else "")
        name_text = self.big_font.render(name_display, True, CYAN)
        controls = self.font.render("ENTER to save, ESC to cancel", True, WHITE)

        title_rect = title.get_rect(center=(self.current_width//2, self.current_height//2 - 100))
        instruction_rect = instruction.get_rect(center=(self.current_width//2, self.current_height//2 - 40))
        name_rect = name_text.get_rect(center=(self.current_width//2, self.current_height//2))
        controls_rect = controls.get_rect(center=(self.current_width//2, self.current_height//2 + 60))

        self.screen.blit(title, title_rect)
        self.screen.blit(instruction, instruction_rect)
        self.screen.blit(name_text, name_rect)
        self.screen.blit(controls, controls_rect)

        # Draw input box
        input_rect = pygame.Rect(self.current_width//2 - 150, self.current_height//2 - 15, 300, 30)
        pygame.draw.rect(self.screen, WHITE, input_rect, 2)

    def draw_leaderboard(self):
        title = self.big_font.render("LEADERBOARD", True, WHITE)
        title_rect = title.get_rect(center=(self.current_width//2, 80))
        self.screen.blit(title, title_rect)

        scores = self.get_top_scores()
        if not scores:
            no_scores = self.font.render("No scores yet!", True, WHITE)
            no_scores_rect = no_scores.get_rect(center=(self.current_width//2, self.current_height//2))
            self.screen.blit(no_scores, no_scores_rect)
        else:
            headers = ["#", "Name", "Score", "Wave", "Date"]
            header_y = 140
            for i, header in enumerate(headers):
                x_positions = [150, 300, 450, 550, 700]
                header_text = self.font.render(header, True, YELLOW)
                self.screen.blit(header_text, (x_positions[i], header_y))

            for i, score_data in enumerate(scores[:10]):
                y = header_y + 40 + i * 30
                rank = f"{i+1}"
                name = score_data["name"][:15]  # Limit name length
                score = f"{score_data['score']}"
                wave = f"{score_data['wave']}"
                date = score_data["date"][:10]  # Show only date part

                data = [rank, name, score, wave, date]
                for j, text_data in enumerate(data):
                    x_positions = [150, 300, 450, 550, 700]
                    color = CYAN if i == 0 else WHITE  # Highlight first place
                    text = self.font.render(str(text_data), True, color)
                    self.screen.blit(text, (x_positions[j], y))

        back_text = self.font.render("Press ESC to return to menu", True, WHITE)
        back_rect = back_text.get_rect(center=(self.current_width//2, self.current_height - 50))
        self.screen.blit(back_text, back_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()

            if self.state == GameState.PLAYING:
                self.update_game(dt)
            elif self.state == GameState.ENTER_NAME:
                self.cursor_timer += dt

            self.screen.fill(BLACK)
            self.draw_stars()

            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.player.draw(self.screen)

                for bullet in self.bullets:
                    bullet.draw(self.screen)
                for bullet in self.enemy_bullets:
                    bullet.draw(self.screen)
                for enemy in self.enemies:
                    enemy.draw(self.screen)
                for power_up in self.power_ups:
                    power_up.draw(self.screen)
                for particle in self.particles:
                    particle.draw(self.screen)

                self.draw_ui()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.VICTORY:
                self.draw_victory()
            elif self.state == GameState.LEADERBOARD:
                self.draw_leaderboard()
            elif self.state == GameState.ENTER_NAME:
                self.draw_enter_name()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CosmicDefender()
    game.run()