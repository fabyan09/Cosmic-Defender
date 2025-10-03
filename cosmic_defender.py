import pygame
import random
import math
import sys
import json
import os
import uuid
import base64
import threading
from datetime import datetime
from enum import Enum

# Optional import for web features
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

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
    PLAYING_INFINITE = 3
    GAME_OVER = 4
    VICTORY = 5
    LEADERBOARD = 6
    ENTER_NAME = 7
    GITHUB_CONFIG = 8
    PAUSED = 9
    RULES = 10
    SETTINGS = 11

class PowerUpType(Enum):
    RAPID_FIRE = 1
    SHIELD = 2
    MULTI_SHOT = 3
    LASER = 4

class Button:
    def __init__(self, x, y, width, height, text, font, color=WHITE, bg_color=None, hover_color=CYAN):
        self.rect = pygame.Rect(x - width//2, y - height//2, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_clicked = False

    def update(self, mouse_pos, mouse_clicked):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.is_clicked = self.is_hovered and mouse_clicked
        return self.is_clicked

    def draw(self, screen):
        # Draw background if specified
        if self.bg_color:
            pygame.draw.rect(screen, self.bg_color, self.rect)

        # Draw border
        border_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, border_color, self.rect, 3)

        # Draw text
        text_color = self.hover_color if self.is_hovered else self.color
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

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
    def __init__(self, x, y, velocity, damage=1, color=YELLOW, is_player_bullet=True):
        self.x = x
        self.y = y
        self.vx, self.vy = velocity
        self.damage = damage
        self.color = color
        self.rect = pygame.Rect(x-2, y-2, 4, 8)
        self.is_player_bullet = is_player_bullet
        self.trail = []  # Trail positions (only for enemy bullets)
        self.trail_max_length = 8

    def update(self, dt, screen_width, screen_height):
        # Add current position to trail (only for enemy bullets)
        if not self.is_player_bullet:
            self.trail.append((self.x, self.y))
            if len(self.trail) > self.trail_max_length:
                self.trail.pop(0)

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rect.center = (int(self.x), int(self.y))
        return 0 <= self.x <= screen_width and 0 <= self.y <= screen_height

    def draw(self, screen):
        # Draw trail only for enemy bullets
        if not self.is_player_bullet:
            for i, (trail_x, trail_y) in enumerate(self.trail):
                alpha = (i + 1) / len(self.trail)
                trail_color = tuple(int(c * alpha) for c in self.color)
                trail_size = int(2 * alpha) + 1
                pygame.draw.circle(screen, trail_color, (int(trail_x), int(trail_y)), trail_size)

        # Draw main bullet
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

        # Load enemy images based on type
        if enemy_type == "tank":
            self.health = 3
            self.speed = 50
            self.size = 30
            self.color = (150, 0, 0)
            self.points = 25
            self.image = pygame.image.load("assets/Enemies/Designs - Base/PNGs/Nairan - Frigate - Base.png")
            self.image = pygame.transform.scale(self.image, (90, 90))  # +50%
            self.max_health = 3
            self.frames = None
            self.destruction_frames = None
            self.is_destroyed = False
        elif enemy_type == "fast":
            self.speed = 200
            self.size = 15
            self.color = (255, 100, 100)
            self.shoot_cooldown = 1.5
            self.points = 15
            self.image = pygame.image.load("assets/Enemies/Designs - Base/PNGs/Nairan - Scout - Base.png")  # Corrigé
            self.image = pygame.transform.scale(self.image, (60, 60))  # +50%
            self.max_health = 1
            self.frames = None
            self.destruction_frames = None
            self.is_destroyed = False
        elif enemy_type == "boss":
            self.health = 20
            self.speed = 30
            self.size = 50
            self.color = (100, 0, 100)
            self.shoot_cooldown = 0.5
            self.points = 100
            self.max_health = 20

            # Load battlecruiser animation (9 frames)
            battlecruiser_spritesheet = pygame.image.load("assets/Enemies/Weapons/PNGs/Nairan - Battlecruiser - Weapons.png")
            sheet_width = battlecruiser_spritesheet.get_width()
            frame_width = sheet_width // 9
            frame_height = battlecruiser_spritesheet.get_height()
            self.frames = []
            for i in range(9):
                frame = battlecruiser_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (150, 150))
                self.frames.append(frame)
            self.frame_index = 0
            self.animation_timer = 0
            self.animation_speed = 0.08

            # Load destruction animation (18 frames)
            destruction_spritesheet = pygame.image.load("assets/Enemies/Destruction/PNGs/Nairan - Battlecruiser  -  Destruction.png")
            sheet_width = destruction_spritesheet.get_width()
            frame_width = sheet_width // 18
            frame_height = destruction_spritesheet.get_height()
            self.destruction_frames = []
            for i in range(18):
                frame = destruction_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (150, 150))
                self.destruction_frames.append(frame)
            self.is_destroyed = False
            self.destruction_frame_index = 0
            self.destruction_animation_timer = 0
            self.destruction_animation_speed = 0.05
        else:  # basic/scout
            self.image = pygame.image.load("assets/Enemies/Designs - Base/PNGs/Nairan - Fighter - Base.png")  # Corrigé
            self.image = pygame.transform.scale(self.image, (60, 60))  # +50%
            self.max_health = 1
            self.frames = None
            self.destruction_frames = None
            self.is_destroyed = False

        self.rect = pygame.Rect(x-self.size//2, y-self.size//2, self.size, self.size)

    def update(self, dt, player_x, player_y, screen_height):
        # If in destruction animation, just update animation
        if self.is_destroyed:
            self.destruction_animation_timer += dt
            if self.destruction_animation_timer >= self.destruction_animation_speed:
                self.destruction_animation_timer = 0
                self.destruction_frame_index += 1
                if self.destruction_frame_index >= 18:
                    return False  # Animation finished, remove enemy
            return True  # Keep enemy to show destruction animation

        if self.enemy_type == "boss":
            self.y += self.speed * dt * 0.5
            self.x += math.sin(self.y * 0.01) * 50 * dt

            # Update animation for boss
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % 9
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
        if self.health <= 0:
            # Start destruction animation if available
            if self.destruction_frames:
                self.is_destroyed = True
                return False  # Don't remove yet, play animation first
            return True  # Remove immediately if no destruction animation
        return False

    def draw(self, screen):
        # Draw destruction animation if destroyed
        if self.is_destroyed and self.destruction_frames:
            if self.destruction_frame_index < len(self.destruction_frames):
                current_frame = self.destruction_frames[self.destruction_frame_index]
                image_rect = current_frame.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(current_frame, image_rect)
            return

        # Draw enemy image or animation
        if self.frames:
            # Draw animation for boss
            current_frame = self.frames[self.frame_index]
            image_rect = current_frame.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(current_frame, image_rect)
        else:
            # Draw static image for other enemies
            image_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.image, image_rect)

        # Draw health bar for boss (not during destruction)
        if self.enemy_type == "boss" and not self.is_destroyed:
            bar_width = 80
            bar_height = 6
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.size - 15

            health_ratio = self.health / self.max_health
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * health_ratio, bar_height))
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

class PowerUp:
    # Class variable to store loaded animations
    _animations_loaded = False
    _shield_frames = []
    _rapid_fire_frames = []
    _laser_frames = []
    _multi_shot_frames = []

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

        # Load all animations once
        if not PowerUp._animations_loaded:
            # Load shield animation
            shield_spritesheet = pygame.image.load("assets/Shield Generators/PNGs/Pickup Icon - Shield Generator - All around shield.png")
            sheet_width = shield_spritesheet.get_width()
            frame_width = sheet_width // 15  # 15 frames
            frame_height = shield_spritesheet.get_height()
            for i in range(15):
                frame = shield_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (40, 40))  # Scale to powerup size
                PowerUp._shield_frames.append(frame)

            # Load rapid fire animation (auto cannons)
            rapid_spritesheet = pygame.image.load("assets/Weapons/PNGs/Pickup Icon - Weapons - Auto Cannons.png")
            sheet_width = rapid_spritesheet.get_width()
            frame_width = sheet_width // 15
            frame_height = rapid_spritesheet.get_height()
            for i in range(15):
                frame = rapid_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (40, 40))
                PowerUp._rapid_fire_frames.append(frame)

            # Load laser animation (big space gun)
            laser_spritesheet = pygame.image.load("assets/Weapons/PNGs/Pickup Icon - Weapons - Big Space Gun 2000.png")
            sheet_width = laser_spritesheet.get_width()
            frame_width = sheet_width // 15
            frame_height = laser_spritesheet.get_height()
            for i in range(15):
                frame = laser_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (40, 40))
                PowerUp._laser_frames.append(frame)

            # Load multi-shot animation (rocket)
            multi_spritesheet = pygame.image.load("assets/Weapons/PNGs/Pickup Icon - Weapons - Rocket.png")
            sheet_width = multi_spritesheet.get_width()
            frame_width = sheet_width // 15
            frame_height = multi_spritesheet.get_height()
            for i in range(15):
                frame = multi_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (40, 40))
                PowerUp._multi_shot_frames.append(frame)

            PowerUp._animations_loaded = True

        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.05  # Time per frame

    def update(self, dt, screen_height):
        self.float_offset += dt * 3
        self.y += 50 * dt
        self.rect.center = (int(self.x), int(self.y + math.sin(self.float_offset) * 3))

        # Update animation for all power-ups
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 15

        return self.y < screen_height + 20

    def draw(self, screen):
        y_pos = int(self.y + math.sin(self.float_offset) * 3)

        # Select the appropriate frame list based on power-up type
        frames = None
        if self.type == PowerUpType.SHIELD:
            frames = PowerUp._shield_frames
        elif self.type == PowerUpType.RAPID_FIRE:
            frames = PowerUp._rapid_fire_frames
        elif self.type == PowerUpType.LASER:
            frames = PowerUp._laser_frames
        elif self.type == PowerUpType.MULTI_SHOT:
            frames = PowerUp._multi_shot_frames

        if frames:
            # Draw animated power-up
            current_frame = frames[self.frame_index]
            frame_rect = current_frame.get_rect(center=(int(self.x), y_pos))
            screen.blit(current_frame, frame_rect)
        else:
            # Fallback to circles if no animation
            pygame.draw.circle(screen, self.color, (int(self.x), y_pos), self.size)
            pygame.draw.circle(screen, WHITE, (int(self.x), y_pos), self.size, 2)

class Player:
    def __init__(self, x, y, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = 300

        # Load ship image
        self.image = pygame.image.load("assets/Main Ship - Bases/PNGs/Main Ship - Base - Full health.png")
        self.image = pygame.transform.scale(self.image, (48, 48))  # Adjust size as needed
        self.size = 24  # Half of image size for collision

        # Load shield animation
        shield_spritesheet = pygame.image.load("assets/Main Ship - Shields/PNGs/Main Ship - Shields - Round Shield.png")
        self.shield_frames = []
        frame_width = 64  # 768 / 12 frames
        frame_height = 64
        for i in range(12):
            frame = shield_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (72, 72))  # Scale up
            self.shield_frames.append(frame)
        self.shield_frame_index = 0
        self.shield_animation_timer = 0
        self.shield_animation_speed = 0.05  # Time per frame

        self.health = 100

        # Trail system
        self.trail = []
        self.trail_max_length = 15
        self.trail_timer = 0
        self.trail_spawn_rate = 0.02  # Spawn trail every 0.02s
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

        # Dash system
        self.dash_speed = 800
        self.dash_distance = 150
        self.dash_cooldown = 2.0
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_direction = (0, 0)

    def update_screen_bounds(self, width, height):
        self.screen_width = width
        self.screen_height = height

    def update(self, dt, joystick=None):
        keys = pygame.key.get_pressed()

        # Update dash cooldown timer
        if self.dash_timer > 0:
            self.dash_timer -= dt

        # Check if player is moving
        is_moving = False
        move_x = 0
        move_y = 0

        # Handle dash movement
        if self.is_dashing:
            # Calculate dash movement with bounds checking
            dash_move_x = self.dash_direction[0] * self.dash_speed * dt
            dash_move_y = self.dash_direction[1] * self.dash_speed * dt

            new_x = self.x + dash_move_x
            new_y = self.y + dash_move_y

            # Clamp to screen bounds
            new_x = max(self.size, min(self.screen_width - self.size, new_x))
            new_y = max(self.size, min(self.screen_height - self.size, new_y))

            self.x = new_x
            self.y = new_y

            # Check if dash is complete
            if self.dash_timer <= self.dash_cooldown - 0.2:  # Dash lasts 0.2s
                self.is_dashing = False
            is_moving = True
        else:
            # Normal movement
            # Keyboard input
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move_x -= 1
                is_moving = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move_x += 1
                is_moving = True
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                move_y -= 1
                is_moving = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                move_y += 1
                is_moving = True

            # Controller input (analog stick)
            if joystick:
                axis_x = joystick.get_axis(0)  # Left stick horizontal
                axis_y = joystick.get_axis(1)  # Left stick vertical

                # Apply deadzone
                deadzone = 0.15
                if abs(axis_x) > deadzone:
                    move_x += axis_x
                    is_moving = True
                if abs(axis_y) > deadzone:
                    move_y += axis_y
                    is_moving = True

            # Apply movement
            self.x += move_x * self.speed * dt
            self.y += move_y * self.speed * dt

            self.x = max(self.size, min(self.screen_width - self.size, self.x))
            self.y = max(self.size, min(self.screen_height - self.size, self.y))

        self.rect.center = (int(self.x), int(self.y))
        self.shoot_timer += dt

        # Update shield animation
        if self.shield > 0:
            self.shield_animation_timer += dt
            if self.shield_animation_timer >= self.shield_animation_speed:
                self.shield_animation_timer = 0
                self.shield_frame_index = (self.shield_frame_index + 1) % 12

        # Update trail
        self.trail_timer += dt
        if is_moving and self.trail_timer >= self.trail_spawn_rate:
            self.trail.append({
                'x': self.x,
                'y': self.y,
                'age': 0,
                'lifetime': 0.3
            })
            self.trail_timer = 0

        # Update and remove old trail particles
        for particle in self.trail[:]:
            particle['age'] += dt
            if particle['age'] >= particle['lifetime']:
                self.trail.remove(particle)

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

    def can_dash(self):
        return self.dash_timer <= 0 and not self.is_dashing

    def dash(self, direction_x, direction_y):
        if self.can_dash():
            # Normalize direction
            length = math.sqrt(direction_x**2 + direction_y**2)
            if length > 0:
                self.dash_direction = (direction_x / length, direction_y / length)
                self.is_dashing = True
                self.dash_timer = self.dash_cooldown
                return True
        return False

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
        # Draw trail first (behind player)
        for particle in self.trail:
            alpha = 1 - (particle['age'] / particle['lifetime'])
            trail_color = tuple(int(c * alpha * 0.6) for c in GREEN)
            trail_size = int(self.size * alpha * 0.5)
            if trail_size > 0:
                pygame.draw.circle(screen, trail_color, (int(particle['x']), int(particle['y'])), trail_size)

        # Draw shield animation if active
        if self.shield > 0:
            current_frame = self.shield_frames[self.shield_frame_index]
            shield_rect = current_frame.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(current_frame, shield_rect)

        color = GREEN
        if self.rapid_fire_timer > 0:
            color = ORANGE
        elif self.multi_shot_timer > 0:
            color = GREEN
        elif self.laser_timer > 0:
            color = PURPLE

        # Draw ship image
        image_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, image_rect)

        # Draw dash cooldown bar
        if self.dash_timer > 0:
            bar_width = 40
            bar_height = 4
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.size - 15

            # Background bar (gray)
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

            # Cooldown progress (white)
            progress = max(0, 1 - (self.dash_timer / self.dash_cooldown))
            progress_width = int(bar_width * progress)
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, progress_width, bar_height))

class GigaBoss:
    def __init__(self, x, y, wave):
        self.x = x
        self.y = y
        self.wave = wave
        self.health = 50 + (wave // 10) * 25  # Health increases with waves
        self.max_health = self.health
        self.speed = 20
        self.size = 80
        self.color = (150, 0, 150)
        self.shoot_timer = 0
        self.pattern_timer = 0
        self.current_pattern = 0
        self.pattern_duration = 3.0
        self.points = 500 + (wave // 10) * 100
        self.rect = pygame.Rect(x-self.size//2, y-self.size//2, self.size, self.size)

        # Load dreadnought animation (34 frames)
        dreadnought_spritesheet = pygame.image.load("assets/Enemies/Weapons/PNGs/Nairan - Dreadnought - Weapons.png")
        sheet_width = dreadnought_spritesheet.get_width()
        frame_width = sheet_width // 34
        frame_height = dreadnought_spritesheet.get_height()
        self.frames = []
        for i in range(34):
            frame = dreadnought_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (240, 240))  # +50% from 160
            self.frames.append(frame)
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.05

        # Load destruction animation (18 frames)
        destruction_spritesheet = pygame.image.load("assets/Enemies/Destruction/PNGs/Nairan - Dreadnought -  Destruction.png")
        sheet_width = destruction_spritesheet.get_width()
        frame_width = sheet_width // 18
        frame_height = destruction_spritesheet.get_height()
        self.destruction_frames = []
        for i in range(18):
            frame = destruction_spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (240, 240))
            self.destruction_frames.append(frame)
        self.is_destroyed = False
        self.destruction_frame_index = 0
        self.destruction_animation_timer = 0
        self.destruction_animation_speed = 0.05

        # Movement pattern
        self.center_x = x
        self.movement_timer = 0
        self.direction = 1

    def update(self, dt, player_x, player_y, screen_width, screen_height):
        # If in destruction animation, just update animation
        if self.is_destroyed:
            self.destruction_animation_timer += dt
            if self.destruction_animation_timer >= self.destruction_animation_speed:
                self.destruction_animation_timer = 0
                self.destruction_frame_index += 1
                if self.destruction_frame_index >= 18:
                    return False  # Animation finished, remove boss
            return True  # Keep boss to show destruction animation

        # Movement pattern - side to side
        self.movement_timer += dt
        self.x = self.center_x + math.sin(self.movement_timer * 0.5) * 200
        self.x = max(self.size, min(screen_width - self.size, self.x))

        # Slowly move down
        self.y += self.speed * dt * 0.3

        self.rect.center = (int(self.x), int(self.y))

        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 34

        # Pattern timing
        self.pattern_timer += dt
        if self.pattern_timer >= self.pattern_duration:
            self.pattern_timer = 0
            self.current_pattern = (self.current_pattern + 1) % 4

        self.shoot_timer += dt
        return self.y < screen_height + 100

    def get_bullets(self, player_x, player_y):
        bullets = []
        if self.shoot_timer < 0.1:  # High fire rate
            return bullets

        self.shoot_timer = 0

        if self.current_pattern == 0:  # Spray pattern
            for i in range(-2, 3):
                angle = math.atan2(player_y - self.y, player_x - self.x) + i * 0.3
                velocity = (math.cos(angle) * 300, math.sin(angle) * 300)
                bullets.append(Bullet(self.x, self.y + 30, velocity, color=PURPLE, is_player_bullet=False))

        elif self.current_pattern == 1:  # Circle pattern
            for i in range(8):
                angle = (i / 8) * 2 * math.pi + self.pattern_timer
                velocity = (math.cos(angle) * 200, math.sin(angle) * 200)
                bullets.append(Bullet(self.x, self.y + 30, velocity, color=RED, is_player_bullet=False))

        elif self.current_pattern == 2:  # Aimed burst
            for _ in range(3):
                angle = math.atan2(player_y - self.y, player_x - self.x) + random.uniform(-0.2, 0.2)
                velocity = (math.cos(angle) * 400, math.sin(angle) * 400)
                bullets.append(Bullet(self.x, self.y + 30, velocity, color=ORANGE, is_player_bullet=False))

        else:  # Laser-like vertical shots
            for i in range(-1, 2):
                velocity = (i * 100, 350)
                bullets.append(Bullet(self.x + i * 50, self.y + 30, velocity, color=YELLOW, is_player_bullet=False))

        return bullets

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_destroyed = True
            return False  # Don't remove yet, play animation first
        return False

    def draw(self, screen):
        # Draw destruction animation if destroyed
        if self.is_destroyed:
            if self.destruction_frame_index < len(self.destruction_frames):
                current_frame = self.destruction_frames[self.destruction_frame_index]
                image_rect = current_frame.get_rect(center=(int(self.x), int(self.y)))
                screen.blit(current_frame, image_rect)
            return

        # Draw dreadnought animation
        current_frame = self.frames[self.frame_index]
        image_rect = current_frame.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(current_frame, image_rect)

        # Health bar (not during destruction)
        bar_width = self.size * 2
        bar_height = 8
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size - 40  # Adjusted for larger sprite

        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

class GitHubUploader:
    def __init__(self):
        # Configuration centralisée - tous les joueurs uploadent vers le même leaderboard
        self.config = {
            "username": "fabyan09",
            "repository": "cosmic-defender-leaderboard",
            "token": self._get_secure_token(),
            "auto_upload": True,
            "configured": True
        }

    def _get_secure_token(self):
        """Récupère le token chiffré de façon sécurisée"""
        try:
            from secure_token import SecureToken
            st = SecureToken()
            token = st.get_embedded_token()
            if token:
                return token
        except ImportError:
            pass
        except Exception as e:
            print(f"Erreur lors du déchiffrement du token: {e}")

        # Fallback: essayer l'ancien système (config_token.py)
        try:
            from config_token import ENCODED_TOKEN
            if ENCODED_TOKEN and ENCODED_TOKEN != "REMPLACEZ_PAR_VOTRE_TOKEN_ENCODE":
                return base64.b64decode(ENCODED_TOKEN.encode()).decode()
        except:
            pass

        return ""

    def is_configured(self):
        """Check if GitHub integration is properly configured"""
        # Vérifie que tous les champs nécessaires sont présents et que requests est disponible
        return (bool(self.config.get("token", "")) and
                bool(self.config.get("username", "")) and
                bool(self.config.get("repository", "")) and
                HAS_REQUESTS)

    def test_connection(self):
        """Test GitHub API connection"""
        if not HAS_REQUESTS or not self.config.get("token"):
            return False, "Requests module or token missing"

        try:
            headers = {
                "Authorization": f"token {self.config['token']}",
                "Accept": "application/vnd.github.v3+json"
            }

            url = f"https://api.github.com/repos/{self.config['username']}/{self.config['repository']}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return True, "Connection successful"
            elif response.status_code == 404:
                return False, "Repository not found"
            elif response.status_code == 401:
                return False, "Invalid token"
            else:
                return False, f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except requests.exceptions.ConnectionError:
            return False, "No internet connection"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def upload_leaderboard(self, new_score_data):
        """Upload leaderboard data to GitHub repository with merge support"""
        if not self.is_configured() or not self.config.get("auto_upload", False):
            return False, "Not configured or auto-upload disabled"

        try:
            headers = {
                "Authorization": f"token {self.config['token']}",
                "Accept": "application/vnd.github.v3+json"
            }

            file_url = f"https://api.github.com/repos/{self.config['username']}/{self.config['repository']}/contents/cosmic_defender_leaderboard.json"

            # Step 1: Download existing leaderboard
            sha = None
            existing_scores = []
            try:
                get_response = requests.get(file_url, headers=headers, timeout=10)
                if get_response.status_code == 200:
                    response_data = get_response.json()
                    sha = response_data.get('sha')

                    # Decode existing content
                    existing_content = base64.b64decode(response_data['content']).decode('utf-8')
                    existing_data = json.loads(existing_content)
                    existing_scores = existing_data.get('scores', [])
                    print(f"📥 Downloaded {len(existing_scores)} existing scores from GitHub")
            except Exception as e:
                print(f"⚠ No existing file or error downloading: {e}")
                # File doesn't exist yet, that's ok

            # Step 2: Merge new score(s) with existing scores
            if 'scores' in new_score_data:
                # Add all new scores to existing list
                existing_scores.extend(new_score_data['scores'])
            else:
                # Handle single score format
                existing_scores.append(new_score_data)

            # Step 3: Sort by score (descending) and limit to top 250
            existing_scores.sort(key=lambda x: x.get('score', 0), reverse=True)
            existing_scores = existing_scores[:250]  # Keep top 250 scores

            # Step 4: Prepare merged data
            merged_data = {
                "last_updated": datetime.now().isoformat(),
                "total_scores": len(existing_scores),
                "scores": existing_scores
            }

            print(f"📊 Merged leaderboard: {len(existing_scores)} total scores")

            # Step 5: Encode and upload
            json_content = json.dumps(merged_data, ensure_ascii=False, indent=2)
            content_encoded = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')

            payload = {
                "message": f"Update leaderboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {len(existing_scores)} scores",
                "content": content_encoded,
                "committer": {
                    "name": "Cosmic Defender",
                    "email": "cosmic-defender@game.local"
                }
            }

            if sha:
                payload["sha"] = sha

            # Upload the merged file
            response = requests.put(file_url, headers=headers, json=payload, timeout=30)

            if response.status_code in [200, 201]:
                return True, f"Upload successful - {len(existing_scores)} scores"
            else:
                return False, f"Upload failed: HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            return False, "Upload timeout"
        except requests.exceptions.ConnectionError:
            return False, "No internet connection"
        except Exception as e:
            return False, f"Upload error: {str(e)}"

    def upload_async(self, leaderboard_data):
        """Upload leaderboard data asynchronously"""
        def upload_thread():
            success, message = self.upload_leaderboard(leaderboard_data)
            if success:
                print("✓ Leaderboard uploaded to GitHub successfully!")
            else:
                print(f"✗ GitHub upload failed: {message}")

        if self.is_configured() and self.config.get("auto_upload", False):
            thread = threading.Thread(target=upload_thread, daemon=True)
            thread.start()

class CosmicDefender:
    def __init__(self):
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Cosmic Defender")
        self.clock = pygame.time.Clock()
        self.running = True

        # Controller/Gamepad support
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Controller detected: {self.joystick.get_name()}")

        # Current screen dimensions (updated when switching modes)
        self.current_width = SCREEN_WIDTH
        self.current_height = SCREEN_HEIGHT

        self.state = GameState.MENU
        self.game_mode = "normal"  # "normal" or "infinite"
        self.player = Player(self.current_width // 2, self.current_height - 100, self.current_width, self.current_height)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.giga_boss = None
        self.power_ups = []
        self.particles = []

        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_per_wave = 10
        self.spawn_timer = 0
        self.spawn_cooldown = 1.0
        self.enemies_killed = 0

        # Pause state
        self.previous_state = None
        self.pause_buttons = []

        # Screen shake
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_intensity = 0
        self.shake_duration = 0

        # Background themes
        self.current_background = 0
        self.background_colors = [
            (10, 10, 30),      # Dark blue - Space
            (30, 10, 30),      # Purple - Nebula
            (10, 30, 30),      # Cyan - Ice field
            (30, 20, 10),      # Orange - Sun zone
            (5, 5, 5),         # Black - Deep space
        ]

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 72)
        self.stars = [(random.randint(0, self.current_width), random.randint(0, self.current_height)) for _ in range(min(200, max(100, self.current_width // 10)))]

        # Score system
        self.scores_file = "scores.json"
        self.web_scores_file = "web_scores.json"
        self.player_name = ""
        self.name_input_active = False
        self.cursor_timer = 0

        # Generate unique player ID for web leaderboard
        self.player_id = self.get_or_create_player_id()

        # GitHub integration (before menu buttons)
        self.github_uploader = GitHubUploader() if HAS_REQUESTS else None

        # Control settings
        self.controls = self.load_controls()
        self.waiting_for_key = None  # Track which control is being rebound
        self.settings_buttons = []

        # Menu buttons (after GitHub uploader is initialized)
        self.menu_buttons = []
        self.create_menu_buttons()

    def create_menu_buttons(self):
        button_width = 300
        button_height = 50
        center_x = self.current_width // 2
        # Adjust start_y to be lower to avoid overlap with title
        start_y = max(self.current_height // 2 - 20, 250)

        self.menu_buttons = [
            Button(center_x, start_y - 90, button_width, button_height, "CAMPAIGN MODE", self.font),
            Button(center_x, start_y - 30, button_width, button_height, "INFINITE MODE", self.font),
            Button(center_x, start_y + 30, button_width, button_height, "SETTINGS", self.font),
            Button(center_x, start_y + 90, button_width, button_height, "RULES", self.font),
            Button(center_x, start_y + 150, button_width, button_height, "LEADERBOARD", self.font),
            Button(center_x, start_y + 210, button_width, button_height, "QUIT", self.font)
        ]

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.current_width, self.current_height = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            self.current_width, self.current_height = SCREEN_WIDTH, SCREEN_HEIGHT

        # Regenerate stars for new screen size
        self.stars = [(random.randint(0, self.current_width), random.randint(0, self.current_height)) for _ in range(min(200, max(100, self.current_width // 10)))]

        # Update player bounds
        if hasattr(self, 'player') and self.player:
            self.player.update_screen_bounds(self.current_width, self.current_height)

        # Recreate menu buttons for new screen size
        self.create_menu_buttons()

    def load_scores(self):
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []

    def save_score(self, name, score, wave, mode="normal"):
        scores = self.load_scores()
        new_score = {
            "name": name,
            "score": score,
            "wave": wave,
            "mode": mode,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        scores.append(new_score)
        scores.sort(key=lambda x: x["score"], reverse=True)
        scores = scores[:20]  # Keep top 20 to accommodate both modes

        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")

    def get_top_scores(self):
        return self.load_scores()[:10]

    def get_or_create_player_id(self):
        id_file = "player_id.txt"
        try:
            if os.path.exists(id_file):
                with open(id_file, 'r') as f:
                    return f.read().strip()
            else:
                player_id = str(uuid.uuid4())
                with open(id_file, 'w') as f:
                    f.write(player_id)
                return player_id
        except:
            return str(uuid.uuid4())

    def load_controls(self):
        """Load control settings from file or return defaults"""
        default_controls = {
            "up": [pygame.K_w, pygame.K_UP],
            "down": [pygame.K_s, pygame.K_DOWN],
            "left": [pygame.K_a, pygame.K_LEFT],
            "right": [pygame.K_d, pygame.K_RIGHT],
            "shoot": [pygame.K_SPACE],
            "pause": [pygame.K_ESCAPE]
        }
        try:
            if os.path.exists("controls.json"):
                with open("controls.json", 'r') as f:
                    return json.load(f)
        except:
            pass
        return default_controls

    def save_controls(self):
        """Save control settings to file"""
        try:
            with open("controls.json", 'w') as f:
                json.dump(self.controls, f, indent=2)
        except Exception as e:
            print(f"Error saving controls: {e}")

    def save_web_score(self, name, score, wave, mode):
        """Save score in web-compatible format to scores directory"""
        web_score = {
            "player_id": self.player_id,
            "name": name,
            "score": score,
            "wave": wave,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        # Create scores directory if it doesn't exist
        scores_dir = "scores"
        os.makedirs(scores_dir, exist_ok=True)

        # Save individual score file (for GitHub Actions to pick up)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        score_filename = os.path.join(scores_dir, f"score_{self.player_id}_{timestamp_str}.json")

        try:
            with open(score_filename, 'w', encoding='utf-8') as f:
                json.dump(web_score, f, ensure_ascii=False, indent=2)
            print(f"✓ Score saved to {score_filename}")
        except Exception as e:
            print(f"Error saving score file: {e}")

        # Also maintain local web_scores.json for backwards compatibility
        web_scores = []
        try:
            if os.path.exists(self.web_scores_file):
                with open(self.web_scores_file, 'r', encoding='utf-8') as f:
                    web_scores = json.load(f)
        except:
            pass

        web_scores.append(web_score)
        web_scores.sort(key=lambda x: x["score"], reverse=True)

        try:
            with open(self.web_scores_file, 'w', encoding='utf-8') as f:
                json.dump(web_scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving web scores: {e}")

        return web_score

    def export_for_github(self, single_score=None):
        """Export scores in format ready for GitHub Pages (deprecated - now using GitHub Actions)"""
        # This method is kept for backwards compatibility but no longer uploads directly
        # Scores are now saved to scores/ directory and uploaded via GitHub Actions
        pass

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

    def spawn_giga_boss(self):
        x = self.current_width // 2
        y = -100
        self.giga_boss = GigaBoss(x, y, self.wave)

    def spawn_power_up(self, x, y):
        if random.random() < 0.3:
            power_type = random.choice(list(PowerUpType))
            self.power_ups.append(PowerUp(x, y, power_type))

    def create_explosion(self, x, y, color=ORANGE, count=10):
        for _ in range(count):
            velocity = (random.uniform(-200, 200), random.uniform(-200, 200))
            self.particles.append(Particle(x, y, color, velocity, random.uniform(0.5, 1.5)))

    def add_screen_shake(self, intensity, duration=0.2):
        """Add screen shake effect"""
        self.shake_intensity = intensity
        self.shake_duration = duration

        # Controller rumble/vibration
        if self.joystick:
            try:
                # Normalize intensity (0.0 to 1.0)
                rumble_intensity = min(intensity / 20.0, 1.0)
                # Rumble with low and high frequency motors
                self.joystick.rumble(rumble_intensity, rumble_intensity, int(duration * 1000))
            except:
                pass  # Some controllers don't support rumble

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                self.current_width, self.current_height = event.w, event.h
                self.screen = pygame.display.set_mode((self.current_width, self.current_height), pygame.RESIZABLE)
                # Regenerate stars for new screen size
                self.stars = [(random.randint(0, self.current_width), random.randint(0, self.current_height)) for _ in range(min(200, max(100, self.current_width // 10)))]
                # Update player bounds
                if hasattr(self, 'player') and self.player:
                    self.player.update_screen_bounds(self.current_width, self.current_height)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_clicked = True
            elif event.type == pygame.JOYBUTTONDOWN:
                # Controller START button (usually button 7 or 9)
                if event.button in [7, 9]:  # START button
                    if self.state in [GameState.PLAYING, GameState.PLAYING_INFINITE]:
                        # Pause the game
                        self.previous_state = self.state
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        # Resume the game
                        self.state = self.previous_state
                        self.previous_state = None
                # Dash with A button (Xbox) / X button (PS) - Button 0
                elif event.button == 0:  # A/X button
                    if self.state in [GameState.PLAYING, GameState.PLAYING_INFINITE]:
                        # Get current stick direction for dash
                        if self.joystick:
                            axis_x = self.joystick.get_axis(0)
                            axis_y = self.joystick.get_axis(1)
                            deadzone = 0.15
                            dash_x = axis_x if abs(axis_x) > deadzone else 0
                            dash_y = axis_y if abs(axis_y) > deadzone else 0
                            if dash_x != 0 or dash_y != 0:
                                self.player.dash(dash_x, dash_y)
                            else:
                                # If no stick input, dash forward (up)
                                self.player.dash(0, -1)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                # Handle ENTER_NAME state first to prioritize text input
                if self.state == GameState.ENTER_NAME:
                    if event.key == pygame.K_ESCAPE:
                        self.player_name = ""
                        self.name_input_active = False
                        self.state = GameState.MENU
                    elif event.key == pygame.K_RETURN and len(self.player_name.strip()) > 0:
                        self.save_score(self.player_name.strip(), self.score, self.wave, self.game_mode)
                        web_score = self.save_web_score(self.player_name.strip(), self.score, self.wave, self.game_mode)

                        # Upload automatique vers GitHub
                        if self.github_uploader and self.github_uploader.is_configured():
                            print("\n" + "="*60)
                            print("📤 Upload automatique du score vers GitHub...")
                            self.github_uploader.upload_async({"scores": [web_score]})
                            print("="*60 + "\n")
                        else:
                            print("\n⚠️  GitHub non configuré - score sauvegardé localement uniquement\n")

                        self.player_name = ""
                        self.name_input_active = False
                        self.state = GameState.LEADERBOARD
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    elif len(self.player_name) < 20 and event.unicode.isprintable():
                        self.player_name += event.unicode
                elif event.key == pygame.K_ESCAPE:
                    if self.fullscreen:
                        self.toggle_fullscreen()
                    elif self.state in [GameState.PLAYING, GameState.PLAYING_INFINITE]:
                        # Pause the game
                        self.previous_state = self.state
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        # Resume the game
                        self.state = self.previous_state
                        self.previous_state = None
                    elif self.state in [GameState.LEADERBOARD, GameState.RULES, GameState.SETTINGS]:
                        self.state = GameState.MENU
                    elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                        self.state = GameState.MENU
                elif event.key == pygame.K_r:
                    # Quick Restart (but not during name entry)
                    if self.state in [GameState.PLAYING, GameState.PLAYING_INFINITE, GameState.PAUSED]:
                        # Restart with the same mode
                        self.start_game(self.game_mode)
                    elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                        # Restart with the same mode
                        self.start_game(self.game_mode)
                elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    # Dash with keyboard (SHIFT key)
                    if self.state in [GameState.PLAYING, GameState.PLAYING_INFINITE]:
                        keys = pygame.key.get_pressed()
                        dash_x = 0
                        dash_y = 0
                        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                            dash_x = -1
                        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                            dash_x = 1
                        if keys[pygame.K_UP] or keys[pygame.K_w]:
                            dash_y = -1
                        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                            dash_y = 1
                        if dash_x != 0 or dash_y != 0:
                            self.player.dash(dash_x, dash_y)
                elif self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.start_game("normal")
                    elif event.key == pygame.K_l:  # L for Leaderboard
                        self.state = GameState.LEADERBOARD
                elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                    if event.key == pygame.K_s:  # S to save score
                        self.player_name = ""
                        self.name_input_active = True
                        self.state = GameState.ENTER_NAME
                elif self.state == GameState.SETTINGS:
                    # Handle key rebinding if waiting for input
                    if self.waiting_for_key:
                        # Rebind the key
                        self.controls[self.waiting_for_key] = [event.key]
                        self.save_controls()
                        self.waiting_for_key = None

        # Handle menu button clicks
        if self.state == GameState.MENU:
            for i, button in enumerate(self.menu_buttons):
                button.update(mouse_pos, mouse_clicked)
                if button.is_clicked:
                    if i == 0:  # Campaign Mode
                        self.start_game("normal")
                    elif i == 1:  # Infinite Mode
                        self.start_game("infinite")
                    elif i == 2:  # Settings
                        self.state = GameState.SETTINGS
                    elif i == 3:  # Rules
                        self.state = GameState.RULES
                    elif i == 4:  # Leaderboard
                        import webbrowser
                        webbrowser.open("https://fabyan09.github.io/cosmic-defender-leaderboard/")
                    elif i == 5:  # Quit
                        self.running = False
        # Handle pause menu button clicks
        elif self.state == GameState.PAUSED:
            for i, button in enumerate(self.pause_buttons):
                button.update(mouse_pos, mouse_clicked)
                if button.is_clicked:
                    if i == 0:  # Resume
                        self.state = self.previous_state
                        self.previous_state = None
                    elif i == 1:  # Main Menu
                        self.state = GameState.MENU
                        self.pause_buttons = []  # Reset pause buttons
        # Handle settings button clicks
        elif self.state == GameState.SETTINGS:
            control_names = list(["up", "down", "left", "right", "shoot", "pause"])

            # Handle button clicks
            for i, button in enumerate(self.settings_buttons):
                button.update(mouse_pos, mouse_clicked)
                if button.is_clicked:
                    if i < len(control_names):
                        # Change control button clicked
                        self.waiting_for_key = control_names[i]
                    elif i == len(control_names):
                        # Reset to defaults
                        self.controls = {
                            "up": [pygame.K_w, pygame.K_UP],
                            "down": [pygame.K_s, pygame.K_DOWN],
                            "left": [pygame.K_a, pygame.K_LEFT],
                            "right": [pygame.K_d, pygame.K_RIGHT],
                            "shoot": [pygame.K_SPACE],
                            "pause": [pygame.K_ESCAPE]
                        }
                        self.save_controls()
                        self.waiting_for_key = None
        else:
            # Update button hover states even if not clicked
            for button in self.menu_buttons:
                button.update(mouse_pos, False)

    def handle_github_config_input(self, event):
        """Handle input in GitHub configuration screen"""
        if not self.github_uploader:
            return

        if event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU
            self.create_menu_buttons()  # Refresh menu buttons
        elif event.key == pygame.K_TAB:
            # Switch between fields
            fields = ["username", "repository", "token"]
            current_index = fields.index(self.github_current_field)
            self.github_current_field = fields[(current_index + 1) % len(fields)]
            # Load current value into input field
            self.github_input_field = self.github_uploader.config.get(self.github_current_field, "")
        elif event.key == pygame.K_RETURN:
            # Save current field and move to next
            self.github_uploader.config[self.github_current_field] = self.github_input_field
            fields = ["username", "repository", "token"]
            current_index = fields.index(self.github_current_field)
            if current_index < len(fields) - 1:
                self.github_current_field = fields[current_index + 1]
                self.github_input_field = self.github_uploader.config.get(self.github_current_field, "")
        elif event.key == pygame.K_BACKSPACE:
            self.github_input_field = self.github_input_field[:-1]
        elif event.key == pygame.K_t:
            # Test connection
            self.test_github_connection()
        elif event.key == pygame.K_s:
            # Save configuration
            self.save_github_config()
        elif event.key == pygame.K_a:
            # Toggle auto-upload
            current_auto = self.github_uploader.config.get("auto_upload", False)
            self.github_uploader.config["auto_upload"] = not current_auto
        elif event.unicode.isprintable() and len(self.github_input_field) < 50:
            self.github_input_field += event.unicode

    def test_github_connection(self):
        """Test GitHub connection"""
        if not self.github_uploader:
            self.github_test_result = "GitHub uploader not available"
            return

        # Save current input
        self.github_uploader.config[self.github_current_field] = self.github_input_field

        # Test connection
        success, message = self.github_uploader.test_connection()
        self.github_test_result = message

    def save_github_config(self):
        """Save GitHub configuration"""
        if not self.github_uploader:
            return

        # Save current input
        self.github_uploader.config[self.github_current_field] = self.github_input_field

        # Mark as configured if all required fields are filled
        if (self.github_uploader.config.get("username") and
            self.github_uploader.config.get("repository") and
            self.github_uploader.config.get("token")):
            self.github_uploader.config["configured"] = True
        else:
            self.github_uploader.config["configured"] = False

        # Save to file
        self.github_uploader.save_config()
        self.github_test_result = "Configuration sauvegardée!"

        # Refresh menu buttons to show new status
        self.create_menu_buttons()

    def start_game(self, mode="normal"):
        self.game_mode = mode
        if mode == "infinite":
            self.state = GameState.PLAYING_INFINITE
        else:
            self.state = GameState.PLAYING

        self.player = Player(self.current_width // 2, self.current_height - 100, self.current_width, self.current_height)
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.giga_boss = None
        self.boss_spawned_this_wave = False
        self.power_ups.clear()
        self.particles.clear()
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.spawn_timer = 0

        # Set initial values based on mode
        if mode == "infinite":
            self.enemies_per_wave = 5  # Start with fewer enemies in infinite mode
        else:
            self.enemies_per_wave = 10

    def update_game(self, dt):
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
            if self.shake_duration <= 0:
                self.shake_offset_x = 0
                self.shake_offset_y = 0
                self.shake_intensity = 0
            else:
                self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
                self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)

        self.player.update(dt, self.joystick)

        # Check for shooting (keyboard, mouse, or controller)
        should_shoot = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            should_shoot = True

        # Controller shooting (R2 trigger on Xbox/PS, axis 5 or button 7)
        if self.joystick:
            # Try R2/RT trigger (axis 5 for most controllers)
            try:
                rt_value = self.joystick.get_axis(5)  # Right trigger
                if rt_value > 0.1:  # Trigger is pressed
                    should_shoot = True
            except:
                pass

            # Fallback to R2/RT button if axis not available
            try:
                if self.joystick.get_button(7):  # R2/RT button
                    should_shoot = True
            except:
                pass

        if self.player.can_shoot() and should_shoot:
            self.bullets.extend(self.player.get_bullets())

        self.bullets = [bullet for bullet in self.bullets if bullet.update(dt, self.current_width, self.current_height)]
        self.enemy_bullets = [bullet for bullet in self.enemy_bullets if bullet.update(dt, self.current_width, self.current_height)]

        # Update regular enemies
        for enemy in self.enemies[:]:
            if not enemy.update(dt, self.player.x, self.player.y, self.current_height):
                self.enemies.remove(enemy)
                continue

            if enemy.can_shoot():
                # Only shoot if enemy is within screen bounds
                if 0 <= enemy.x <= self.current_width and 0 <= enemy.y <= self.current_height:
                    angle = math.atan2(self.player.y - enemy.y, self.player.x - enemy.x)
                    velocity = (math.cos(angle) * 200, math.sin(angle) * 200)
                    self.enemy_bullets.append(Bullet(enemy.x, enemy.y, velocity, color=RED, is_player_bullet=False))

        # Update giga boss
        if self.giga_boss:
            if not self.giga_boss.update(dt, self.player.x, self.player.y, self.current_width, self.current_height):
                self.giga_boss = None
            else:
                # Giga boss shooting
                giga_bullets = self.giga_boss.get_bullets(self.player.x, self.player.y)
                self.enemy_bullets.extend(giga_bullets)

        self.power_ups = [power_up for power_up in self.power_ups if power_up.update(dt, self.current_height)]
        self.particles = [particle for particle in self.particles if particle.update(dt)]

        # Bullet vs enemies collision
        for bullet in self.bullets[:]:
            hit = False
            # Check collision with regular enemies
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if enemy.take_damage(bullet.damage):
                        self.score += enemy.points
                        self.enemies_killed += 1
                        self.create_explosion(enemy.x, enemy.y)
                        self.add_screen_shake(3, 0.1)  # Small shake for normal enemies
                        self.spawn_power_up(enemy.x, enemy.y)
                        self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    hit = True
                    break

            # Check collision with giga boss
            if not hit and self.giga_boss and bullet.rect.colliderect(self.giga_boss.rect):
                if self.giga_boss.take_damage(bullet.damage):
                    self.score += self.giga_boss.points
                    self.enemies_killed += 1
                    self.create_explosion(self.giga_boss.x, self.giga_boss.y, PURPLE, 20)
                    self.add_screen_shake(15, 0.4)  # Big shake for boss death
                    self.spawn_power_up(self.giga_boss.x, self.giga_boss.y)
                    self.giga_boss = None
                self.bullets.remove(bullet)

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

        # Player collision with enemies
        for enemy in self.enemies[:]:
            if enemy.rect.colliderect(self.player.rect):
                if self.player.take_damage(10):
                    self.state = GameState.GAME_OVER
                self.create_explosion(self.player.x, self.player.y, RED)
                self.enemies.remove(enemy)

        # Player collision with giga boss
        if self.giga_boss and self.giga_boss.rect.colliderect(self.player.rect):
            if self.player.take_damage(20):
                self.state = GameState.GAME_OVER
            self.create_explosion(self.player.x, self.player.y, RED)

        # Wave management
        if self.game_mode == "infinite":
            # In infinite mode, check for giga boss every 10 waves
            if self.wave % 10 == 0 and not self.giga_boss and not self.boss_spawned_this_wave and len(self.enemies) == 0 and self.enemies_spawned >= self.enemies_per_wave:
                self.spawn_giga_boss()
                self.boss_spawned_this_wave = True
            elif not self.giga_boss:  # Normal enemy spawning when no giga boss
                self.spawn_timer += dt
                # Increase max enemies on screen as waves progress in infinite mode
                max_enemies = min(30, 15 + (self.wave // 2))
                if (self.spawn_timer >= self.spawn_cooldown and
                    self.enemies_spawned < self.enemies_per_wave and
                    len(self.enemies) < max_enemies):
                    self.spawn_enemy()
                    self.enemies_spawned += 1
                    self.spawn_timer = 0

            # Wave progression in infinite mode
            if self.enemies_spawned >= self.enemies_per_wave and len(self.enemies) == 0 and not self.giga_boss:
                self.wave += 1
                self.enemies_spawned = 0
                self.boss_spawned_this_wave = False
                # Increase difficulty more aggressively: +2 base + wave/5 for exponential growth
                self.enemies_per_wave += 2 + (self.wave // 5)
                self.spawn_cooldown = max(0.15, self.spawn_cooldown - 0.03)
                # Change background every 10 waves
                if self.wave % 10 == 0:
                    self.current_background = (self.current_background + 1) % len(self.background_colors)
        else:
            # Normal campaign mode
            self.spawn_timer += dt
            # Increase max enemies on screen as waves progress
            max_enemies = min(25, 15 + (self.wave // 2))
            if (self.spawn_timer >= self.spawn_cooldown and
                self.enemies_spawned < self.enemies_per_wave and
                len(self.enemies) < max_enemies):
                self.spawn_enemy()
                self.enemies_spawned += 1
                self.spawn_timer = 0

            if self.enemies_spawned >= self.enemies_per_wave and len(self.enemies) == 0:
                self.wave += 1
                self.enemies_spawned = 0
                # Increase difficulty more: +3 base + wave/3 for good progression
                self.enemies_per_wave += 3 + (self.wave // 3)
                self.spawn_cooldown = max(0.25, self.spawn_cooldown - 0.06)
                # Change background every 10 waves
                if self.wave % 10 == 0:
                    self.current_background = (self.current_background + 1) % len(self.background_colors)

                if self.wave > 10:
                    self.state = GameState.VICTORY

    def draw_offscreen_indicators(self):
        """Draw arrows pointing to off-screen enemies"""
        margin = 30
        indicator_size = 15

        for enemy in self.enemies:
            # Check if enemy is off-screen
            if enemy.x < 0 or enemy.x > self.current_width or enemy.y < 0:
                # Calculate arrow position at screen edge
                arrow_x = max(margin, min(self.current_width - margin, enemy.x))
                arrow_y = max(margin, min(self.current_height - margin, enemy.y))

                # Calculate direction to enemy
                angle = math.atan2(enemy.y - arrow_y, enemy.x - arrow_x)

                # Draw arrow pointing to enemy
                arrow_color = enemy.color
                # Arrow triangle
                point1 = (arrow_x + math.cos(angle) * indicator_size,
                         arrow_y + math.sin(angle) * indicator_size)
                point2 = (arrow_x + math.cos(angle + 2.5) * indicator_size * 0.6,
                         arrow_y + math.sin(angle + 2.5) * indicator_size * 0.6)
                point3 = (arrow_x + math.cos(angle - 2.5) * indicator_size * 0.6,
                         arrow_y + math.sin(angle - 2.5) * indicator_size * 0.6)

                pygame.draw.polygon(self.screen, arrow_color, [point1, point2, point3])
                pygame.draw.polygon(self.screen, WHITE, [point1, point2, point3], 2)

        # Do the same for giga boss
        if self.giga_boss:
            if self.giga_boss.x < 0 or self.giga_boss.x > self.current_width or self.giga_boss.y < 0:
                arrow_x = max(margin, min(self.current_width - margin, self.giga_boss.x))
                arrow_y = max(margin, min(self.current_height - margin, self.giga_boss.y))

                angle = math.atan2(self.giga_boss.y - arrow_y, self.giga_boss.x - arrow_x)

                # Bigger arrow for boss
                boss_indicator_size = 25
                arrow_color = PURPLE
                point1 = (arrow_x + math.cos(angle) * boss_indicator_size,
                         arrow_y + math.sin(angle) * boss_indicator_size)
                point2 = (arrow_x + math.cos(angle + 2.5) * boss_indicator_size * 0.6,
                         arrow_y + math.sin(angle + 2.5) * boss_indicator_size * 0.6)
                point3 = (arrow_x + math.cos(angle - 2.5) * boss_indicator_size * 0.6,
                         arrow_y + math.sin(angle - 2.5) * boss_indicator_size * 0.6)

                pygame.draw.polygon(self.screen, arrow_color, [point1, point2, point3])
                pygame.draw.polygon(self.screen, WHITE, [point1, point2, point3], 3)

    def draw_stars(self):
        for star in self.stars:
            pygame.draw.circle(self.screen, WHITE, star, 1)

    def draw_ui(self):
        health_text = self.font.render(f"Health: {self.player.health}", True, WHITE)
        shield_text = self.font.render(f"Shield: {self.player.shield}", True, CYAN)
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)
        mode_text = self.font.render(f"Mode: {self.game_mode.upper()}", True, YELLOW)

        self.screen.blit(health_text, (10, 10))
        self.screen.blit(shield_text, (10, 50))
        self.screen.blit(score_text, (self.current_width - 150, 10))
        self.screen.blit(wave_text, (self.current_width - 150, 50))
        self.screen.blit(mode_text, (self.current_width - 200, 90))

        # Show giga boss warning
        if self.game_mode == "infinite" and self.wave % 10 == 0 and not self.giga_boss and len(self.enemies) == 0:
            warning_text = self.big_font.render("GIGA BOSS INCOMING!", True, RED)
            warning_rect = warning_text.get_rect(center=(self.current_width//2, self.current_height//2))
            self.screen.blit(warning_text, warning_rect)

        health_bar_width = 200
        health_ratio = self.player.health / self.player.max_health
        health_color = GREEN if health_ratio > 0.5 else ORANGE if health_ratio > 0.25 else RED

        pygame.draw.rect(self.screen, RED, (10, 90, health_bar_width, 10))
        pygame.draw.rect(self.screen, health_color, (10, 90, health_bar_width * health_ratio, 10))

        if self.player.shield > 0:
            shield_ratio = self.player.shield / self.player.max_shield
            pygame.draw.rect(self.screen, CYAN, (10, 105, health_bar_width * shield_ratio, 5))

        # Draw off-screen enemy indicators
        self.draw_offscreen_indicators()

    def draw_menu(self):
        title = self.big_font.render("COSMIC DEFENDER", True, WHITE)
        title_rect = title.get_rect(center=(self.current_width//2, self.current_height//2 - 200))
        self.screen.blit(title, title_rect)

        # Draw menu buttons
        for button in self.menu_buttons:
            button.draw(self.screen)

        # Instructions
        instructions = [
            " ",
            " ",
            "Campaign Mode: Survive 10 waves to win!",
            "Infinite Mode: Endless waves with Giga Bosses every 10 waves!"
        ]

        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(self.current_width//2, self.current_height//2 + 200 + i * 30))
            self.screen.blit(text, text_rect)

    def draw_game_over(self):
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        wave_text = self.font.render(f"Wave Reached: {self.wave}", True, WHITE)
        mode_text = self.font.render(f"Mode: {self.game_mode.upper()}", True, YELLOW)
        restart_text = self.font.render("Press S to save score, R to restart or ESC for menu", True, WHITE)

        texts = [game_over_text, score_text, wave_text, mode_text, restart_text]
        for i, text in enumerate(texts):
            text_rect = text.get_rect(center=(self.current_width//2, self.current_height//2 - 80 + i * 40))
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

    def init_github_config(self):
        """Initialize GitHub configuration interface"""
        self.github_input_field = ""
        self.github_current_field = "username"  # username, repository, token
        self.github_test_result = ""
        self.github_show_password = False

    def draw_github_config(self):
        """Draw GitHub configuration screen"""
        title = self.big_font.render("GITHUB CONFIGURATION", True, WHITE)
        title_rect = title.get_rect(center=(self.current_width//2, 80))
        self.screen.blit(title, title_rect)

        if not HAS_REQUESTS:
            error_text = self.font.render("Erreur: Module 'requests' requis pour GitHub", True, RED)
            error_rect = error_text.get_rect(center=(self.current_width//2, 200))
            self.screen.blit(error_text, error_rect)

            back_text = self.font.render("Appuyez sur ESC pour retourner", True, WHITE)
            back_rect = back_text.get_rect(center=(self.current_width//2, self.current_height - 100))
            self.screen.blit(back_text, back_rect)
            return

        y_offset = 180
        field_height = 60

        # Instructions
        instructions = [
            "1. Créez un token GitHub dans Settings > Developer settings > Personal access tokens",
            "2. Donnez les permissions 'repo' et 'contents:write'",
            "3. Entrez vos informations ci-dessous:"
        ]

        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, YELLOW)
            self.screen.blit(text, (50, 120 + i * 25))

        # Fields
        fields = [
            ("Username GitHub:", "username"),
            ("Nom du repository:", "repository"),
            ("Token d'accès:", "token")
        ]

        for i, (label, field_name) in enumerate(fields):
            y = y_offset + i * field_height

            # Label
            label_text = self.font.render(label, True, WHITE)
            self.screen.blit(label_text, (50, y))

            # Input field
            field_rect = pygame.Rect(250, y, 500, 40)
            field_color = CYAN if self.github_current_field == field_name else WHITE

            # Get field value
            if hasattr(self.github_uploader, 'config'):
                field_value = self.github_uploader.config.get(field_name, "")
            else:
                field_value = ""

            # Show current input or saved value
            if self.github_current_field == field_name:
                display_value = self.github_input_field
            else:
                display_value = field_value

            # Hide token with asterisks
            if field_name == "token" and display_value and not self.github_show_password:
                display_value = "*" * min(len(display_value), 20)

            pygame.draw.rect(self.screen, field_color, field_rect, 2)

            if display_value:
                value_text = self.font.render(display_value[:40], True, WHITE)
                self.screen.blit(value_text, (field_rect.x + 10, field_rect.y + 10))

            # Current field indicator
            if self.github_current_field == field_name:
                cursor_x = field_rect.x + 10 + len(display_value) * 12
                pygame.draw.line(self.screen, CYAN, (cursor_x, field_rect.y + 5), (cursor_x, field_rect.y + 35), 2)

        # Buttons
        button_y = y_offset + len(fields) * field_height + 20

        # Auto-upload checkbox
        auto_upload_enabled = self.github_uploader and self.github_uploader.config.get("auto_upload", False)
        checkbox_color = GREEN if auto_upload_enabled else WHITE
        checkbox_text = "☑" if auto_upload_enabled else "☐"

        checkbox_surface = self.font.render(f"{checkbox_text} Upload automatique", True, checkbox_color)
        self.screen.blit(checkbox_surface, (50, button_y))

        # Test connection button
        test_rect = pygame.Rect(50, button_y + 50, 200, 40)
        pygame.draw.rect(self.screen, GREEN, test_rect, 2)
        test_text = self.font.render("TESTER", True, WHITE)
        test_text_rect = test_text.get_rect(center=test_rect.center)
        self.screen.blit(test_text, test_text_rect)

        # Save button
        save_rect = pygame.Rect(270, button_y + 50, 200, 40)
        pygame.draw.rect(self.screen, BLUE, save_rect, 2)
        save_text = self.font.render("SAUVEGARDER", True, WHITE)
        save_text_rect = save_text.get_rect(center=save_rect.center)
        self.screen.blit(save_text, save_text_rect)

        # Test result
        if self.github_test_result:
            result_color = GREEN if "successful" in self.github_test_result.lower() else RED
            result_text = self.font.render(self.github_test_result, True, result_color)
            self.screen.blit(result_text, (50, button_y + 110))

        # Controls
        controls = [
            "TAB: Changer de champ | ENTER: Valider | ESC: Retour",
            "T: Tester connexion | S: Sauvegarder | A: Toggle auto-upload"
        ]

        for i, control in enumerate(controls):
            text = pygame.font.Font(None, 24).render(control, True, WHITE)
            self.screen.blit(text, (50, self.current_height - 80 + i * 25))

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
            headers = ["#", "Name", "Score", "Wave", "Mode", "Date"]
            header_y = 140
            for i, header in enumerate(headers):
                x_positions = [100, 200, 350, 450, 530, 620]
                header_text = self.font.render(header, True, YELLOW)
                self.screen.blit(header_text, (x_positions[i], header_y))

            for i, score_data in enumerate(scores[:15]):
                y = header_y + 40 + i * 25
                rank = f"{i+1}"
                name = score_data["name"][:12]  # Limit name length
                score = f"{score_data['score']}"
                wave = f"{score_data['wave']}"
                mode = score_data.get("mode", "normal")[:8]  # Backward compatibility
                date = score_data["date"][:10]  # Show only date part

                data = [rank, name, score, wave, mode, date]
                for j, text_data in enumerate(data):
                    x_positions = [100, 200, 350, 450, 530, 620]
                    color = CYAN if i == 0 else WHITE  # Highlight first place
                    text = self.font.render(str(text_data), True, color)
                    self.screen.blit(text, (x_positions[j], y))

        back_text = self.font.render("Press ESC to return to menu", True, WHITE)
        back_rect = back_text.get_rect(center=(self.current_width//2, self.current_height - 50))
        self.screen.blit(back_text, back_rect)

    def draw_pause_menu(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.current_width, self.current_height))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Title
        title = self.big_font.render("PAUSED", True, CYAN)
        title_rect = title.get_rect(center=(self.current_width//2, 80))
        self.screen.blit(title, title_rect)

        # Stats section
        stats_y = 180
        stats_title = self.font.render("CURRENT STATS", True, YELLOW)
        self.screen.blit(stats_title, (self.current_width//2 - stats_title.get_width()//2, stats_y))

        stats_y += 50
        stats = [
            f"Score: {self.score}",
            f"Wave: {self.wave}",
            f"Health: {self.player.health}/{self.player.max_health}",
            f"Mode: {self.game_mode.upper()}",
            f"Enemies Killed: {self.enemies_killed}",
        ]

        for stat in stats:
            stat_text = self.font.render(stat, True, WHITE)
            self.screen.blit(stat_text, (self.current_width//2 - stat_text.get_width()//2, stats_y))
            stats_y += 35

        # Controls section
        controls_y = stats_y + 40
        controls_title = self.font.render("CONTROLS", True, YELLOW)
        self.screen.blit(controls_title, (self.current_width//2 - controls_title.get_width()//2, controls_y))

        controls_y += 50
        controls = [
            "ARROW KEYS / WASD / LEFT STICK - Move",
            "SPACE / MOUSE / R2 TRIGGER - Shoot",
            "SHIFT / A BUTTON (Xbox) / X (PS) - Dash",
            "F - Toggle Fullscreen",
            "ESC / START - Pause / Resume",
            "R - Quick Restart",
        ]

        for control in controls:
            control_text = self.small_font.render(control, True, WHITE)
            self.screen.blit(control_text, (self.current_width//2 - control_text.get_width()//2, controls_y))
            controls_y += 30

        # Create pause menu buttons if not created
        if not self.pause_buttons:
            button_width = 250
            button_height = 50
            center_x = self.current_width // 2
            button_y = self.current_height - 150

            self.pause_buttons = [
                Button(center_x - 140, button_y, button_width, button_height, "RESUME (ESC)", self.font, color=GREEN),
                Button(center_x + 140, button_y, button_width, button_height, "MAIN MENU", self.font, color=ORANGE)
            ]

        # Draw and update buttons
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for button in self.pause_buttons:
            button.update(mouse_pos, mouse_clicked)
            button.draw(self.screen)

    def draw_enemy_preview(self, screen, x, y, enemy_type, size=30):
        """Draw a small preview of an enemy for the rules page - matches actual game sprites"""
        rect = pygame.Rect(x - size//2, y - size//2, size, size)

        if enemy_type == "normal":
            # Normal enemy - red square (from Enemy.draw())
            color = RED
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
        elif enemy_type == "tank":
            # Tank enemy - dark red square (from Enemy.draw())
            color = (150, 0, 0)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
        elif enemy_type == "fast":
            # Fast enemy - pink square (from Enemy.draw())
            color = (255, 100, 100)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 2)
        elif enemy_type == "boss":
            # Boss enemy - purple ellipse (from Enemy.draw())
            color = (100, 0, 100)
            pygame.draw.ellipse(screen, color, rect)
            pygame.draw.ellipse(screen, WHITE, rect, 3)
        elif enemy_type == "gigaboss":
            # Giga Boss - larger purple ellipse with spikes (from GigaBoss.draw())
            color = (150, 0, 150)
            # Main body
            pygame.draw.ellipse(screen, color, rect)
            pygame.draw.ellipse(screen, WHITE, rect, 3)
            # Add spikes
            for i in range(8):
                angle = (i / 8) * 2 * math.pi
                spike_x = rect.centerx + math.cos(angle) * (size // 2 + 5)
                spike_y = rect.centery + math.sin(angle) * (size // 2 + 5)
                pygame.draw.line(screen, color, rect.center, (spike_x, spike_y), 2)

    def draw_rules(self):
        # Title
        title = self.big_font.render("RULES & ENEMIES", True, CYAN)
        title_rect = title.get_rect(center=(self.current_width//2, 50))
        self.screen.blit(title, title_rect)

        # Game objective
        objective_y = 110
        objective = self.font.render("OBJECTIVE: Survive waves and destroy all enemies!", True, YELLOW)
        self.screen.blit(objective, (self.current_width//2 - objective.get_width()//2, objective_y))

        # Enemy types section
        enemies_y = 170
        enemies_title = self.font.render("ENEMY TYPES", True, YELLOW)
        self.screen.blit(enemies_title, (50, enemies_y))

        enemies_y += 50
        enemy_data = [
            {
                "type": "normal",
                "name": "SCOUT",
                "health": "1 HP",
                "speed": "Medium",
                "points": "10",
                "desc": "Basic enemy, moves slowly"
            },
            {
                "type": "fast",
                "name": "INTERCEPTOR",
                "health": "1 HP",
                "speed": "Fast",
                "points": "15",
                "desc": "Quick and agile"
            },
            {
                "type": "tank",
                "name": "DESTROYER",
                "health": "3 HP",
                "speed": "Slow",
                "points": "25",
                "desc": "Armored and durable"
            },
            {
                "type": "boss",
                "name": "COMMANDER",
                "health": "20 HP",
                "speed": "Medium",
                "points": "100",
                "desc": "Fires rapidly, zigzag pattern"
            },
            {
                "type": "gigaboss",
                "name": "TITAN",
                "health": "50+ HP",
                "speed": "Slow",
                "points": "500+",
                "desc": "Wave 10, 20, 30... Massive threat!"
            }
        ]

        for i, enemy in enumerate(enemy_data):
            y_pos = enemies_y + i * 80

            # Draw enemy preview
            self.draw_enemy_preview(self.screen, 80, y_pos + 15, enemy["type"], 30)

            # Enemy name
            name_text = self.font.render(enemy["name"], True, CYAN)
            self.screen.blit(name_text, (130, y_pos - 5))

            # Stats
            stats_text = self.small_font.render(
                f"HP: {enemy['health']}  |  Speed: {enemy['speed']}  |  Points: {enemy['points']}",
                True, WHITE
            )
            self.screen.blit(stats_text, (130, y_pos + 25))

            # Description
            desc_text = self.small_font.render(enemy["desc"], True, (180, 180, 180))
            self.screen.blit(desc_text, (130, y_pos + 48))

        # Power-ups section
        powerups_y = enemies_y + len(enemy_data) * 80 + 20
        if powerups_y < self.current_height - 180:
            powerups_title = self.font.render("POWER-UPS", True, YELLOW)
            self.screen.blit(powerups_title, (50, powerups_y))

            powerups_y += 35
            powerups_text = self.small_font.render("Dropped by enemies - Rapid Fire, Shield, Multi-Shot, Laser", True, WHITE)
            self.screen.blit(powerups_text, (50, powerups_y))

            # Controls section
            powerups_y += 50
            controls_title = self.font.render("CONTROLS", True, YELLOW)
            self.screen.blit(controls_title, (50, powerups_y))

            powerups_y += 35
            controls_texts = [
                "Move: ARROW KEYS / WASD / LEFT STICK",
                "Shoot: SPACE / MOUSE / R2 TRIGGER",
                "Dash: SHIFT / A BUTTON (Xbox) / X (PS) - Evade quickly!"
            ]
            for ctrl_text in controls_texts:
                ctrl_render = self.small_font.render(ctrl_text, True, WHITE)
                self.screen.blit(ctrl_render, (50, powerups_y))
                powerups_y += 25

        # Back button
        button_width = 250
        button_height = 50
        back_button = Button(
            self.current_width//2,
            self.current_height - 50,
            button_width,
            button_height,
            "RETURN TO MENU",
            self.font,
            color=GREEN
        )
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        back_button.update(mouse_pos, mouse_clicked)
        back_button.draw(self.screen)

        # Handle back button click
        if back_button.is_clicked:
            self.state = GameState.MENU

    def draw_settings(self):
        # Title
        title = self.big_font.render("SETTINGS", True, CYAN)
        title_rect = title.get_rect(center=(self.current_width//2, 60))
        self.screen.blit(title, title_rect)

        # Controls section
        controls_y = 150
        controls_title = self.font.render("CONTROLS", True, YELLOW)
        self.screen.blit(controls_title, (self.current_width//2 - controls_title.get_width()//2, controls_y))

        controls_y += 60
        control_names = {
            "up": "Move Up",
            "down": "Move Down",
            "left": "Move Left",
            "right": "Move Right",
            "shoot": "Shoot",
            "pause": "Pause"
        }

        for action, name in control_names.items():
            # Get key names
            keys = self.controls[action]
            key_names = []
            for key in keys:
                key_name = pygame.key.name(key).upper()
                key_names.append(key_name)
            keys_text = " / ".join(key_names)

            # Draw action name
            action_text = self.font.render(f"{name}:", True, WHITE)
            self.screen.blit(action_text, (self.current_width//2 - 250, controls_y))

            # Draw keys
            if self.waiting_for_key == action:
                keys_display = self.font.render("Press a key...", True, YELLOW)
            else:
                keys_display = self.font.render(keys_text, True, CYAN)
            self.screen.blit(keys_display, (self.current_width//2 + 50, controls_y))

            # Create button for rebinding
            if not self.settings_buttons or len(self.settings_buttons) < len(control_names):
                button_width = 150
                button_height = 40
                button = Button(
                    self.current_width//2 + 300,
                    controls_y + 20,
                    button_width,
                    button_height,
                    "Change",
                    self.small_font
                )
                self.settings_buttons.append(button)

            controls_y += 60

        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for i, button in enumerate(self.settings_buttons[:len(control_names)]):
            button.update(mouse_pos, mouse_clicked)
            button.draw(self.screen)

        # Reset to defaults button
        reset_button_y = controls_y + 40
        if len(self.settings_buttons) < len(control_names) + 1:
            reset_btn = Button(
                self.current_width//2,
                reset_button_y,
                250,
                50,
                "Reset to Defaults",
                self.font,
                color=ORANGE
            )
            self.settings_buttons.append(reset_btn)

        if len(self.settings_buttons) > len(control_names):
            self.settings_buttons[-1].update(mouse_pos, mouse_clicked)
            self.settings_buttons[-1].draw(self.screen)

        # Back instruction
        back_text = self.font.render("Press ESC to return", True, GREEN)
        back_rect = back_text.get_rect(center=(self.current_width//2, self.current_height - 40))
        self.screen.blit(back_text, back_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()

            if self.state in [GameState.PLAYING, GameState.PLAYING_INFINITE]:
                self.update_game(dt)
            elif self.state == GameState.ENTER_NAME:
                self.cursor_timer += dt

            # Fill with dynamic background color
            bg_color = self.background_colors[self.current_background]
            self.screen.fill(bg_color)
            self.draw_stars()

            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state in [GameState.PLAYING, GameState.PLAYING_INFINITE]:
                # Create a temporary surface for game elements
                game_surface = pygame.Surface((self.current_width, self.current_height))
                game_surface.fill(bg_color)

                # Draw stars on game surface
                for star in self.stars:
                    pygame.draw.circle(game_surface, WHITE, star, 1)

                self.player.draw(game_surface)

                for bullet in self.bullets:
                    bullet.draw(game_surface)
                for bullet in self.enemy_bullets:
                    bullet.draw(game_surface)
                for enemy in self.enemies:
                    enemy.draw(game_surface)
                if self.giga_boss:
                    self.giga_boss.draw(game_surface)
                for power_up in self.power_ups:
                    power_up.draw(game_surface)
                for particle in self.particles:
                    particle.draw(game_surface)

                # Apply screen shake offset
                self.screen.blit(game_surface, (self.shake_offset_x, self.shake_offset_y))

                self.draw_ui()
            elif self.state == GameState.PAUSED:
                self.draw_pause_menu()
            elif self.state == GameState.RULES:
                self.draw_rules()
            elif self.state == GameState.SETTINGS:
                self.draw_settings()
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