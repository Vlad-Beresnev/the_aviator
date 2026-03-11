"""Pygame 2D survival-shooter action game for THE AVIATOR.

Entry point: run_level(level_number, difficulty, battery)
Returns dict: {"victory": bool, "battery_remaining": int}

Player must survive LEVEL_DURATION seconds.  Battery acts as a health bar —
enemy hits reduce it; reaching 0 means the level is failed.
"""

import os
import sys
import random
import pygame
import config
import sprites


# ---------------------------------------------------------------------------
# Entity classes
# ---------------------------------------------------------------------------

class Player:
    def __init__(self, image: pygame.Surface, x: int, y: int):
        self.image = image
        self.rect = image.get_rect(center=(x, y))
        self.fire_cooldown = 0

    def update(self, keys, bounds: pygame.Rect):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= config.PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += config.PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= config.PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += config.PLAYER_SPEED
        self.rect.x += dx
        self.rect.y += dy
        self.rect.clamp_ip(bounds)
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1

    def can_fire(self) -> bool:
        return self.fire_cooldown <= 0

    def fire(self, bullet_image: pygame.Surface) -> "Bullet":
        self.fire_cooldown = config.PLAYER_FIRE_INTERVAL
        return Bullet(
            bullet_image,
            self.rect.centerx,
            self.rect.top,
            dy=-config.BULLET_SPEED,
        )

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)


class Enemy:
    def __init__(self, image: pygame.Surface, x: int, y: int,
                 speed: float, fire_interval: int):
        self.image = image
        self.rect = image.get_rect(center=(x, y))
        self.speed = speed
        self.fire_interval = fire_interval
        self.fire_timer = random.randint(0, fire_interval)
        # Simple random horizontal drift
        self.drift = random.uniform(-1.5, 1.5)

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.drift
        # Bounce off horizontal edges
        if self.rect.left < 0 or self.rect.right > config.GAME_WIDTH:
            self.drift = -self.drift
        self.fire_timer -= 1

    def can_fire(self) -> bool:
        return self.fire_timer <= 0

    def fire(self, bullet_image: pygame.Surface) -> "Bullet":
        self.fire_timer = self.fire_interval + random.randint(-10, 10)
        return Bullet(
            bullet_image,
            self.rect.centerx,
            self.rect.bottom,
            dy=config.ENEMY_BULLET_SPEED,
        )

    def off_screen(self) -> bool:
        return self.rect.top > config.GAME_HEIGHT + 20

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)


class Bullet:
    def __init__(self, image: pygame.Surface, x: int, y: int, dy: float):
        self.image = image
        self.rect = image.get_rect(center=(x, y))
        self.dy = dy

    def update(self):
        self.rect.y += self.dy

    def off_screen(self) -> bool:
        return self.rect.bottom < -10 or self.rect.top > config.GAME_HEIGHT + 10

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)


class Explosion:
    def __init__(self, frames: list, x: int, y: int):
        self.frames = frames
        self.x = x
        self.y = y
        self.index = 0
        self.timer = 0

    def update(self) -> bool:
        """Advance frame. Return False when animation is done."""
        self.timer += 1
        if self.timer % 4 == 0:
            self.index += 1
        return self.index < len(self.frames)

    def draw(self, surface: pygame.Surface):
        if self.index < len(self.frames):
            img = self.frames[self.index]
            rect = img.get_rect(center=(self.x, self.y))
            surface.blit(img, rect)


# ---------------------------------------------------------------------------
# Pixel-art bitmap text (no font module — avoids circular import on Py 3.14)
# ---------------------------------------------------------------------------

# 3-wide × 5-tall bitmaps, MSB = leftmost column
_BITMAPS: dict[str, list[int]] = {
    '0': [0b111,0b101,0b101,0b101,0b111],
    '1': [0b010,0b110,0b010,0b010,0b111],
    '2': [0b111,0b001,0b111,0b100,0b111],
    '3': [0b111,0b001,0b111,0b001,0b111],
    '4': [0b101,0b101,0b111,0b001,0b001],
    '5': [0b111,0b100,0b111,0b001,0b111],
    '6': [0b111,0b100,0b111,0b101,0b111],
    '7': [0b111,0b001,0b001,0b010,0b010],
    '8': [0b111,0b101,0b111,0b101,0b111],
    '9': [0b111,0b101,0b111,0b001,0b111],
    'A': [0b010,0b101,0b111,0b101,0b101],
    'C': [0b111,0b100,0b100,0b100,0b111],
    'G': [0b111,0b100,0b101,0b101,0b111],
    'H': [0b101,0b101,0b111,0b101,0b101],
    'I': [0b111,0b010,0b010,0b010,0b111],
    'K': [0b101,0b110,0b100,0b110,0b101],
    'L': [0b100,0b100,0b100,0b100,0b111],
    'M': [0b101,0b111,0b101,0b101,0b101],
    'N': [0b101,0b111,0b111,0b101,0b101],
    'O': [0b111,0b101,0b101,0b101,0b111],
    'P': [0b111,0b101,0b111,0b100,0b100],
    'R': [0b111,0b101,0b111,0b110,0b101],
    'S': [0b111,0b100,0b111,0b001,0b111],
    'T': [0b111,0b010,0b010,0b010,0b010],
    'U': [0b101,0b101,0b101,0b101,0b111],
    'W': [0b101,0b101,0b101,0b111,0b010],
    'Y': [0b101,0b101,0b111,0b010,0b010],
    '!': [0b010,0b010,0b010,0b000,0b010],
    ' ': [0b000,0b000,0b000,0b000,0b000],
}


def _blit_text(surface: pygame.Surface, text: str, x: int, y: int,
               cell: int = 3, color: tuple = (255, 255, 255)) -> int:
    """Draw pixel-art text. Returns x after the last character."""
    for ch in text.upper():
        bmap = _BITMAPS.get(ch, _BITMAPS[' '])
        for row, bits in enumerate(bmap):
            for col in range(3):
                if bits & (1 << (2 - col)):
                    pygame.draw.rect(surface, color,
                                     (x + col * cell, y + row * cell, cell, cell))
        x += 4 * cell
    return x


# ---------------------------------------------------------------------------
# HUD drawing
# ---------------------------------------------------------------------------

def _draw_hud(surface: pygame.Surface, battery: int, max_battery: int,
              time_left: float, level: int, km_left: float, total_km: float):
    """Draw battery bar, km progress bar, and countdown timer."""
    bar_h = 20
    bar_y = 10
    side_w = 175  # width of left/right bars

    # ── Battery bar (left) ────────────────────────────────────────────────
    bat_x = 10
    pygame.draw.rect(surface, (40, 40, 40), (bat_x, bar_y, side_w, bar_h))
    fill_ratio = max(0, battery / max_battery)
    fill_colour = (0, 200, 80) if fill_ratio > 0.4 else (
        (255, 180, 0) if fill_ratio > 0.15 else (220, 40, 40)
    )
    pygame.draw.rect(surface, fill_colour, (bat_x, bar_y, int(side_w * fill_ratio), bar_h))
    pygame.draw.rect(surface, (220, 220, 220), (bat_x, bar_y, side_w, bar_h), 2)
    _blit_text(surface, "FUEL", bat_x + 4, bar_y + 5, cell=2, color=(255, 255, 255))

    # ── Timer bar (right) ─────────────────────────────────────────────────
    tbar_x = config.GAME_WIDTH - side_w - 10
    timer_ratio = max(0, time_left / config.LEVEL_DURATION)
    pygame.draw.rect(surface, (40, 40, 40), (tbar_x, bar_y, side_w, bar_h))
    t_colour = (80, 160, 255) if timer_ratio > 0.3 else (255, 120, 0)
    pygame.draw.rect(surface, t_colour, (tbar_x, bar_y, int(side_w * timer_ratio), bar_h))
    pygame.draw.rect(surface, (220, 220, 220), (tbar_x, bar_y, side_w, bar_h), 2)
    _blit_text(surface, "TIME", tbar_x + 4, bar_y + 5, cell=2, color=(255, 255, 255))

    # ── KM progress bar (centre) ──────────────────────────────────────────
    km_x = bat_x + side_w + 8
    km_w = tbar_x - km_x - 8
    pygame.draw.rect(surface, (25, 25, 50), (km_x, bar_y, km_w, bar_h))
    km_ratio = max(0, km_left / total_km) if total_km > 0 else 0
    km_col = (0, 200, 255) if km_ratio > 0.5 else (
        (255, 220, 0) if km_ratio > 0.2 else (255, 90, 0)
    )
    pygame.draw.rect(surface, km_col, (km_x, bar_y, int(km_w * km_ratio), bar_h))
    pygame.draw.rect(surface, (180, 180, 230), (km_x, bar_y, km_w, bar_h), 2)
    km_str = f"{int(km_left)} KM"
    km_text_w = len(km_str) * 4 * 2
    _blit_text(surface, km_str,
               km_x + (km_w - km_text_w) // 2, bar_y + 5,
               cell=2, color=(255, 255, 255))


# ---------------------------------------------------------------------------
# Main game loop
# ---------------------------------------------------------------------------

def run_level(level_number: int, difficulty: int, battery: int) -> dict:
    """
    Run a single action-game level.

    Args:
        level_number: 1-based level index (affects enemy scaling)
        difficulty: 1-5 difficulty rating from goal table
        battery: current battery (health) value

    Returns:
        {"victory": bool, "battery_remaining": int}
    """
    pygame.init()
    screen = pygame.display.set_mode((config.GAME_WIDTH, config.GAME_HEIGHT))
    pygame.display.set_caption(f"THE AVIATOR — Level {level_number}")

    # Bring game window to front on macOS
    if sys.platform == "darwin":
        try:
            from AppKit import NSApp, NSApplication
            NSApplication.sharedApplication()
            NSApp.activateIgnoringOtherApps_(True)
        except ImportError:
            import subprocess
            subprocess.Popen([
                "osascript", "-e",
                'tell application "System Events" to set frontmost '
                'of the first process whose unix id is '
                + str(os.getpid()) + ' to true'
            ])

    clock = pygame.time.Clock()

    # Scaling factors based on difficulty and level (base — ramps during play)
    scale = 1.0 + (difficulty - 1) * 0.25 + (level_number - 1) * 0.08
    base_enemy_speed = config.ENEMY_BASE_SPEED * (0.8 + scale * 0.4)
    base_spawn_interval = max(10, int(config.ENEMY_BASE_SPAWN_INTERVAL / scale))
    base_fire_interval = max(15, int(config.ENEMY_BASE_FIRE_INTERVAL / scale))
    # Current values (updated during gameplay for progressive difficulty)
    enemy_speed = base_enemy_speed
    spawn_interval = base_spawn_interval
    fire_interval = base_fire_interval

    # Assets
    bg = sprites.make_background(config.GAME_WIDTH, config.GAME_HEIGHT)
    bg_y = 0  # scrolling offset
    # Sprites generated at final size — no scaling needed.
    player_img = sprites.make_player(96)
    enemy_imgs = [sprites.make_enemy(v, 84) for v in range(3)]
    bullet_player_img = sprites.make_bullet_player()
    bullet_enemy_img = sprites.make_bullet_enemy()
    explosion_frames = sprites.make_explosion_frames()

    # Entities
    player = Player(player_img, config.GAME_WIDTH // 2, config.GAME_HEIGHT - 60)
    enemies: list[Enemy] = []
    player_bullets: list[Bullet] = []
    enemy_bullets: list[Bullet] = []
    explosions: list[Explosion] = []

    spawn_timer = 0
    max_battery = config.MAX_BATTERY
    current_battery = battery
    duration_frames = config.LEVEL_DURATION * config.FPS
    frame = 0
    bounds = pygame.Rect(0, 0, config.GAME_WIDTH, config.GAME_HEIGHT)
    total_km = 450.0                                      # total flight distance
    passive_drain_per_frame = 0.33 * max_battery / duration_frames  # 33% over full level
    passive_drain_acc = 0.0                               # accumulator for sub-integer drain
    km_left = total_km                                    # updated each frame

    running = True
    victory = False

    while running:
        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        if not running:
            break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
            break

        # --- Update player ---
        player.update(keys, bounds)

        # Auto-fire or space-fire
        if keys[pygame.K_SPACE] and player.can_fire():
            player_bullets.append(player.fire(bullet_player_img))
        elif player.can_fire():
            # Auto-fire at slower rate when not pressing space
            if frame % (config.PLAYER_FIRE_INTERVAL * 3) == 0:
                player_bullets.append(player.fire(bullet_player_img))

        # --- Spawn enemies (difficulty ramps up as time passes) ---
        progress = frame / duration_frames   # 0..1
        ramp = 1.0 + progress * 0.6          # up to +60% harder by end
        enemy_speed = base_enemy_speed * ramp
        spawn_interval = max(8, int(base_spawn_interval / ramp))
        fire_interval = max(12, int(base_fire_interval / ramp))

        spawn_timer += 1
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            ex = random.randint(20, config.GAME_WIDTH - 20)
            variant = random.randint(0, 2)
            enemies.append(Enemy(
                enemy_imgs[variant], ex, -30,
                speed=enemy_speed + random.uniform(-0.5, 0.5),
                fire_interval=fire_interval,
            ))

        # --- Update enemies ---
        for e in enemies:
            e.update()
            if e.can_fire():
                enemy_bullets.append(e.fire(bullet_enemy_img))

        enemies = [e for e in enemies if not e.off_screen()]

        # --- Update bullets ---
        for b in player_bullets:
            b.update()
        for b in enemy_bullets:
            b.update()
        player_bullets = [b for b in player_bullets if not b.off_screen()]
        enemy_bullets = [b for b in enemy_bullets if not b.off_screen()]

        # --- Collisions: player bullets vs enemies ---
        remaining_enemies = []
        for e in enemies:
            hit = False
            for b in player_bullets:
                if e.rect.colliderect(b.rect):
                    hit = True
                    player_bullets.remove(b)
                    explosions.append(Explosion(explosion_frames, e.rect.centerx, e.rect.centery))
                    break
            if not hit:
                remaining_enemies.append(e)
        enemies = remaining_enemies

        # --- Collisions: enemy bullets vs player ---
        for b in enemy_bullets[:]:
            if b.rect.colliderect(player.rect):
                current_battery -= config.HIT_DAMAGE
                enemy_bullets.remove(b)
                if current_battery <= 0:
                    current_battery = 0
                    explosions.append(Explosion(explosion_frames, player.rect.centerx, player.rect.centery))

        # --- Collisions: enemies crashing into player ---
        for e in enemies[:]:
            if e.rect.colliderect(player.rect):
                current_battery -= config.HIT_DAMAGE * 2
                enemies.remove(e)
                explosions.append(Explosion(explosion_frames, e.rect.centerx, e.rect.centery))
                if current_battery <= 0:
                    current_battery = 0

        # --- Passive fuel drain (33% over full level) ---
        passive_drain_acc += passive_drain_per_frame
        drained = int(passive_drain_acc)
        if drained > 0:
            current_battery = max(0, current_battery - drained)
            passive_drain_acc -= drained

        # --- Update explosions ---
        explosions = [ex for ex in explosions if ex.update()]

        # --- Check end conditions ---
        if current_battery <= 0:
            # Flash red then close window
            overlay = pygame.Surface((config.GAME_WIDTH, config.GAME_HEIGHT))
            overlay.fill((180, 0, 0))
            for _ in range(20):
                pygame.event.pump()
                screen.blit(bg, (0, 0))
                for ex in explosions:
                    ex.update()
                    ex.draw(screen)
                screen.blit(overlay, (0, 0))
                _draw_hud(screen, 0, max_battery, 0, level_number, km_left, total_km)
                pygame.display.flip()
                clock.tick(config.FPS)
            running = False
            victory = False
            break

        frame += 1
        time_left = max(0, (duration_frames - frame) / config.FPS)
        km_left = total_km * time_left / config.LEVEL_DURATION

        if frame >= duration_frames:
            # ── Victory: confetti + pixel-art congratulations ──────────────
            rng_c = random.Random(7)
            confetti = [
                (rng_c.randint(0, config.GAME_WIDTH),
                 rng_c.randint(-config.GAME_HEIGHT, config.GAME_HEIGHT),
                 rng_c.randint(5, 14), rng_c.randint(4, 9),
                 rng_c.choice([(255,50,50),(255,215,0),(0,220,50),
                               (0,150,255),(220,0,255),(255,150,0)]),
                 rng_c.uniform(1.8, 4.5), rng_c.uniform(-2.0, 2.0))
                for _ in range(90)
            ]
            dark = pygame.Surface((config.GAME_WIDTH, config.GAME_HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 130))
            msg = "CONGRATULATIONS!"
            cell = 4
            msg_w = len(msg) * 4 * cell
            msg_x = (config.GAME_WIDTH - msg_w) // 2
            msg_y = config.GAME_HEIGHT // 2 - 20
            for ticker in range(120):   # ~1.6 s at 75 fps
                pygame.event.pump()
                bg_y_v = (bg_y + ticker) % config.GAME_HEIGHT
                screen.blit(bg, (0, bg_y_v))
                screen.blit(bg, (0, bg_y_v - config.GAME_HEIGHT))
                screen.blit(dark, (0, 0))
                for (cx, cy0, cw, ch, cc, cvy, cvx) in confetti:
                    draw_cy = int((cy0 + ticker * cvy) % (config.GAME_HEIGHT + 200) - 100)
                    draw_cx = int((cx + ticker * cvx) % config.GAME_WIDTH)
                    pygame.draw.rect(screen, cc, (draw_cx, draw_cy, cw, ch))
                # Shadow
                _blit_text(screen, msg, msg_x + 2, msg_y + 2, cell=cell, color=(0, 0, 0))
                # Main text — pulsing gold/white
                pulse = (255, 255, int(100 + 155 * abs(((ticker * 6) % 360 - 180) / 180)))
                _blit_text(screen, msg, msg_x, msg_y, cell=cell, color=pulse)
                _draw_hud(screen, current_battery, max_battery, 0, level_number, 0, total_km)
                pygame.display.flip()
                clock.tick(config.FPS)
            running = False
            victory = True
            break

        # --- Draw ---
        # Scrolling background
        bg_y = (bg_y + 1) % config.GAME_HEIGHT
        screen.blit(bg, (0, bg_y))
        screen.blit(bg, (0, bg_y - config.GAME_HEIGHT))

        for e in enemies:
            e.draw(screen)
        for b in player_bullets:
            b.draw(screen)
        for b in enemy_bullets:
            b.draw(screen)
        for ex in explosions:
            ex.draw(screen)
        player.draw(screen)

        _draw_hud(screen, current_battery, max_battery, time_left, level_number, km_left, total_km)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.display.quit()
    pygame.quit()

    return {"victory": victory, "battery_remaining": max(0, current_battery)}
