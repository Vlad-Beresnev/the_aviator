"""Programmatic pixel-art sprite generator for THE AVIATOR action game.

All sprites are produced as pygame.Surface objects — no external image files required.
"""

import pygame


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
SKY_BLUE = (135, 206, 235)
DARK_BLUE = (20, 30, 80)
WHITE = (255, 255, 255)
CLOUD_WHITE = (240, 240, 255)
GREEN = (0, 200, 80)
RED = (220, 40, 40)
ORANGE = (255, 140, 0)
YELLOW = (255, 220, 0)
GREY = (160, 160, 160)
DARK_GREY = (80, 80, 80)
PLAYER_BODY = (40, 120, 200)
PLAYER_WING = (30, 90, 170)
PLAYER_COCKPIT = (200, 220, 255)
ENEMY_BODY_1 = (180, 40, 40)
ENEMY_WING_1 = (140, 30, 30)
ENEMY_BODY_2 = (50, 160, 50)
ENEMY_WING_2 = (30, 120, 30)
ENEMY_BODY_3 = (160, 100, 40)
ENEMY_WING_3 = (130, 80, 30)


def _set_px(surface: pygame.Surface, x: int, y: int, colour: tuple) -> None:
    """Set a single pixel, bounds-checked."""
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), colour)


# ---------------------------------------------------------------------------
# Player plane  (32×32, top-down view, pointing UP)
# ---------------------------------------------------------------------------

def make_player(size: int = 96) -> pygame.Surface:
    """Return a player plane surface (top-down, nose up) with detailed shapes."""
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2
    f = size / 96  # scale factor

    def r(v):
        return int(v * f)

    body = PLAYER_BODY
    wing = PLAYER_WING
    cockpit = PLAYER_COCKPIT
    dark = (20, 60, 130)
    highlight = (70, 160, 240)

    # Drop shadow (subtle, semi-transparent)
    shadow = pygame.Surface((size, size), pygame.SRCALPHA)
    shadow_pts = [
        (cx + r(3), r(8)), (cx + r(8), r(42)), (cx + r(44), r(46)),
        (cx + r(8), r(54)), (cx + r(10), r(78)), (cx + r(3), r(82)),
        (cx - r(3), r(82)), (cx - r(10), r(78)), (cx - r(8), r(54)),
        (cx - r(44), r(46)), (cx - r(8), r(42)), (cx - r(3), r(8)),
    ]
    pygame.draw.polygon(shadow, (0, 0, 0, 35), shadow_pts)

    # ── Fuselage (tapered body)
    fuse_pts = [
        (cx, r(6)),                          # nose tip
        (cx + r(5), r(18)),
        (cx + r(7), r(38)),
        (cx + r(8), r(55)),
        (cx + r(10), r(75)),                 # rear widening
        (cx + r(6), r(85)),                  # tail
        (cx - r(6), r(85)),
        (cx - r(10), r(75)),
        (cx - r(8), r(55)),
        (cx - r(7), r(38)),
        (cx - r(5), r(18)),
    ]
    pygame.draw.polygon(s, body, fuse_pts)
    # Fuselage highlight stripe (left side reflection)
    hl_pts = [
        (cx - r(2), r(10)),
        (cx, r(10)),
        (cx + r(1), r(55)),
        (cx - r(3), r(55)),
    ]
    pygame.draw.polygon(s, highlight, hl_pts)
    # Fuselage dark edge (right)
    de_pts = [
        (cx + r(3), r(18)),
        (cx + r(6), r(18)),
        (cx + r(8), r(55)),
        (cx + r(5), r(55)),
    ]
    pygame.draw.polygon(s, dark, de_pts)

    # ── Main wings (swept-back)
    # Left wing
    lw = [
        (cx - r(6), r(40)),      # root leading edge
        (cx - r(42), r(48)),     # tip leading edge
        (cx - r(44), r(52)),     # tip trailing edge
        (cx - r(8), r(56)),      # root trailing edge
    ]
    pygame.draw.polygon(s, wing, lw)
    pygame.draw.polygon(s, dark, lw, max(1, r(1)))
    # Left wing highlight
    lwh = [
        (cx - r(6), r(41)),
        (cx - r(30), r(46)),
        (cx - r(32), r(48)),
        (cx - r(7), r(48)),
    ]
    pygame.draw.polygon(s, highlight, lwh)

    # Right wing
    rw = [
        (cx + r(6), r(40)),
        (cx + r(42), r(48)),
        (cx + r(44), r(52)),
        (cx + r(8), r(56)),
    ]
    pygame.draw.polygon(s, wing, rw)
    pygame.draw.polygon(s, dark, rw, max(1, r(1)))

    # ── Engine nacelles on wings
    for sign in (-1, 1):
        ex = cx + sign * r(22)
        ey = r(46)
        pygame.draw.ellipse(s, dark, (ex - r(4), ey - r(6), r(8), r(14)))
        pygame.draw.ellipse(s, body, (ex - r(3), ey - r(5), r(6), r(12)))
        # Propeller disc
        pygame.draw.circle(s, (200, 200, 200, 180), (ex, ey - r(6)), r(4))

    # ── Tail wings (horizontal stabilizer)
    for sign in (-1, 1):
        tw = [
            (cx + sign * r(5), r(76)),
            (cx + sign * r(22), r(80)),
            (cx + sign * r(20), r(84)),
            (cx + sign * r(6), r(82)),
        ]
        pygame.draw.polygon(s, wing, tw)
        pygame.draw.polygon(s, dark, tw, max(1, r(1)))

    # Vertical stabilizer (tail fin)
    vt = [
        (cx, r(72)),
        (cx + r(3), r(86)),
        (cx - r(3), r(86)),
    ]
    pygame.draw.polygon(s, dark, vt)
    pygame.draw.polygon(s, body, [
        (cx, r(74)),
        (cx + r(2), r(85)),
        (cx - r(2), r(85)),
    ])

    # ── Cockpit canopy (glass bubble)
    canopy_rect = (cx - r(4), r(16), r(8), r(18))
    pygame.draw.ellipse(s, cockpit, canopy_rect)
    # Glass reflection
    pygame.draw.ellipse(s, (230, 240, 255), (cx - r(2), r(18), r(3), r(8)))

    # Fuselage outline for crispness
    pygame.draw.polygon(s, dark, fuse_pts, max(1, r(1)))

    # Make the plane semi-transparent so terrain is visible beneath it
    alpha_mask = pygame.Surface((size, size), pygame.SRCALPHA)
    alpha_mask.fill((255, 255, 255, 180))  # 180/255 ≈ 70% opacity
    s.blit(alpha_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return s


# ---------------------------------------------------------------------------
# Enemy planes  (28×28, top-down, pointing DOWN)
# ---------------------------------------------------------------------------

_ENEMY_PALETTES = [
    (ENEMY_BODY_1, ENEMY_WING_1, (220, 60, 60), (100, 20, 20)),     # red fighter
    (ENEMY_BODY_2, ENEMY_WING_2, (80, 200, 80), (20, 90, 20)),      # green bomber
    (ENEMY_BODY_3, ENEMY_WING_3, (200, 140, 70), (100, 60, 20)),    # brown prop
]


def make_enemy(variant: int = 0, size: int = 84) -> pygame.Surface:
    """Return an enemy plane surface (top-down, nose DOWN) with detailed shapes."""
    pal = _ENEMY_PALETTES[variant % len(_ENEMY_PALETTES)]
    body, wing, highlight, dark = pal
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2
    f = size / 84

    def r(v):
        return int(v * f)

    # ── Fuselage (nose at bottom)
    fuse = [
        (cx, r(78)),                         # nose tip (bottom)
        (cx + r(5), r(68)),
        (cx + r(7), r(50)),
        (cx + r(8), r(30)),
        (cx + r(6), r(14)),
        (cx + r(3), r(6)),                   # tail top
        (cx - r(3), r(6)),
        (cx - r(6), r(14)),
        (cx - r(8), r(30)),
        (cx - r(7), r(50)),
        (cx - r(5), r(68)),
    ]
    pygame.draw.polygon(s, body, fuse)
    # Highlight stripe
    pygame.draw.polygon(s, highlight, [
        (cx - r(2), r(12)),
        (cx + r(1), r(12)),
        (cx + r(2), r(65)),
        (cx - r(1), r(65)),
    ])
    # Dark edge
    pygame.draw.polygon(s, dark, fuse, max(1, r(1)))

    if variant % 3 == 0:
        # ── Red fighter: sleek swept wings
        for sign in (-1, 1):
            w = [
                (cx + sign * r(6), r(28)),
                (cx + sign * r(38), r(36)),
                (cx + sign * r(40), r(40)),
                (cx + sign * r(7), r(42)),
            ]
            pygame.draw.polygon(s, wing, w)
            pygame.draw.polygon(s, dark, w, max(1, r(1)))
            # Wing highlight
            pygame.draw.polygon(s, highlight, [
                (cx + sign * r(7), r(29)),
                (cx + sign * r(26), r(34)),
                (cx + sign * r(28), r(36)),
                (cx + sign * r(7), r(36)),
            ])

        # Tail wings
        for sign in (-1, 1):
            tw = [
                (cx + sign * r(4), r(10)),
                (cx + sign * r(20), r(6)),
                (cx + sign * r(18), r(12)),
                (cx + sign * r(5), r(14)),
            ]
            pygame.draw.polygon(s, wing, tw)
            pygame.draw.polygon(s, dark, tw, max(1, r(1)))

    elif variant % 3 == 1:
        # ── Green bomber: broad straight wings
        for sign in (-1, 1):
            w = [
                (cx + sign * r(6), r(30)),
                (cx + sign * r(40), r(30)),
                (cx + sign * r(42), r(38)),
                (cx + sign * r(40), r(42)),
                (cx + sign * r(7), r(42)),
            ]
            pygame.draw.polygon(s, wing, w)
            pygame.draw.polygon(s, dark, w, max(1, r(1)))
            # Engine pod
            ex = cx + sign * r(24)
            pygame.draw.ellipse(s, dark, (ex - r(4), r(28), r(8), r(16)))
            pygame.draw.ellipse(s, body, (ex - r(3), r(29), r(6), r(14)))

        # Tail
        for sign in (-1, 1):
            tw = [
                (cx + sign * r(4), r(8)),
                (cx + sign * r(22), r(4)),
                (cx + sign * r(24), r(10)),
                (cx + sign * r(5), r(14)),
            ]
            pygame.draw.polygon(s, wing, tw)
            pygame.draw.polygon(s, dark, tw, max(1, r(1)))

    else:
        # ── Brown prop: rounded biplane-style wings
        for sign in (-1, 1):
            # Upper wing set
            w1 = [
                (cx + sign * r(6), r(24)),
                (cx + sign * r(36), r(24)),
                (cx + sign * r(38), r(30)),
                (cx + sign * r(7), r(30)),
            ]
            pygame.draw.polygon(s, wing, w1)
            pygame.draw.polygon(s, dark, w1, max(1, r(1)))
            # Lower wing set
            w2 = [
                (cx + sign * r(6), r(38)),
                (cx + sign * r(32), r(38)),
                (cx + sign * r(34), r(44)),
                (cx + sign * r(7), r(44)),
            ]
            pygame.draw.polygon(s, wing, w2)
            pygame.draw.polygon(s, dark, w2, max(1, r(1)))
            # Wing struts
            pygame.draw.line(s, dark,
                             (cx + sign * r(18), r(24)),
                             (cx + sign * r(18), r(44)),
                             max(1, r(2)))

        # Tail
        for sign in (-1, 1):
            tw = [
                (cx + sign * r(4), r(8)),
                (cx + sign * r(16), r(6)),
                (cx + sign * r(14), r(12)),
                (cx + sign * r(5), r(12)),
            ]
            pygame.draw.polygon(s, wing, tw)

    # ── Vertical fin
    pygame.draw.polygon(s, dark, [
        (cx, r(4)),
        (cx + r(3), r(14)),
        (cx - r(3), r(14)),
    ])
    pygame.draw.polygon(s, body, [
        (cx, r(5)),
        (cx + r(2), r(13)),
        (cx - r(2), r(13)),
    ])

    # ── Cockpit (glass canopy, toward nose)
    canopy_rect = (cx - r(3), r(56), r(6), r(14))
    pygame.draw.ellipse(s, (180, 200, 180), canopy_rect)
    pygame.draw.ellipse(s, (220, 230, 220), (cx - r(1), r(58), r(2), r(6)))
    pygame.draw.ellipse(s, dark, canopy_rect, max(1, r(1)))

    return s


# ---------------------------------------------------------------------------
# Projectiles
# ---------------------------------------------------------------------------

def make_bullet_player() -> pygame.Surface:
    """Bright 5×10 neon-yellow player rocket — high contrast against any terrain."""
    s = pygame.Surface((5, 10), pygame.SRCALPHA)
    # Bright yellow core
    pygame.draw.rect(s, (255, 255, 0), (1, 0, 3, 10))
    # White hot tip
    pygame.draw.rect(s, (255, 255, 255), (1, 0, 3, 3))
    # Cyan glow edges
    pygame.draw.rect(s, (0, 255, 220), (0, 3, 1, 6))
    pygame.draw.rect(s, (0, 255, 220), (4, 3, 1, 6))
    return s


def make_bullet_enemy() -> pygame.Surface:
    """Bright 5×10 neon-magenta enemy rocket — high contrast against any terrain."""
    s = pygame.Surface((5, 10), pygame.SRCALPHA)
    # Hot magenta core
    pygame.draw.rect(s, (255, 0, 200), (1, 0, 3, 10))
    # White hot tip
    pygame.draw.rect(s, (255, 255, 255), (1, 7, 3, 3))
    # Orange glow edges
    pygame.draw.rect(s, (255, 120, 0), (0, 0, 1, 7))
    pygame.draw.rect(s, (255, 120, 0), (4, 0, 1, 7))
    return s


# ---------------------------------------------------------------------------
# Explosion (simple expanding flash)
# ---------------------------------------------------------------------------

def make_explosion_frames(count: int = 6, max_radius: int = 18) -> list:
    """Return a list of surfaces representing an explosion animation."""
    frames = []
    for i in range(count):
        r = max_radius * (i + 1) // count
        size = max_radius * 2 + 4
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size // 2
        alpha = 255 - (i * 40)
        if alpha < 60:
            alpha = 60
        pygame.draw.circle(s, (*ORANGE, alpha), (cx, cy), r)
        inner = max(1, r // 2)
        pygame.draw.circle(s, (*YELLOW, alpha), (cx, cy), inner)
        frames.append(s)
    return frames


# ---------------------------------------------------------------------------
# Background — scrolling top-down terrain (sea, fields, forests, rivers)
# ---------------------------------------------------------------------------

def make_background(width: int, height: int) -> pygame.Surface:
    """Top-down terrain: sea edges, fields, forests, river, light clouds."""
    import random
    rng = random.Random(42)

    s = pygame.Surface((width, height))

    # ── Base land (grass)
    s.fill((75, 130, 55))

    # ── Left sea strip
    sea_w = 90
    for x in range(sea_w):
        t = x / sea_w
        # blend sea → sandy beach → land
        if t < 0.55:
            c = (int(18 + 20 * t), int(80 + 30 * t), int(185 - 20 * t))
        else:
            fade = (t - 0.55) / 0.45
            c = (int(38 * (1 - fade) + 195 * fade),
                 int(110 * (1 - fade) + 175 * fade),
                 int(165 * (1 - fade) + 100 * fade))
        pygame.draw.line(s, c, (x, 0), (x, height))

    # ── Right sea strip
    for x in range(sea_w):
        t = x / sea_w
        if t < 0.45:
            c = (int(18 + 20 * (1 - t)), int(80 + 30 * (1 - t)), int(185 - 20 * (1 - t)))
        else:
            fade = (t - 0.45) / 0.55
            c = (int(38 * fade + 195 * (1 - fade)),
                 int(110 * fade + 175 * (1 - fade)),
                 int(165 * fade + 100 * (1 - fade)))
        pygame.draw.line(s, c, (width - 1 - x, 0), (width - 1 - x, height))

    # ── Agricultural field patches (rectangles, varied greens/yellows)
    field_colours = [
        (140, 190, 70), (160, 205, 80), (195, 195, 75),
        (175, 160, 55), (120, 170, 55), (105, 155, 50),
    ]
    for _ in range(22):
        fx = rng.randint(sea_w + 5, width - sea_w - 5)
        fy = rng.randint(5, height - 5)
        fw = rng.randint(35, 110)
        fh = rng.randint(25, 70)
        pygame.draw.rect(s, rng.choice(field_colours),
                         (fx - fw // 2, fy - fh // 2, fw, fh))

    # ── Forests (dark green filled circles with lighter highlight)
    for _ in range(18):
        fx = rng.randint(sea_w + 25, width - sea_w - 25)
        fy = rng.randint(20, height - 20)
        fr = rng.randint(18, 45)
        pygame.draw.circle(s, (28, 92, 28), (fx, fy), fr)
        pygame.draw.circle(s, (45, 115, 40), (fx - fr // 4, fy - fr // 4), max(6, fr // 2))

    # ── River (meandering blue ribbon)
    rx = width // 3 + rng.randint(-40, 40)
    prev_rx = rx
    for y in range(0, height, 1):
        rx += rng.randint(-2, 2)
        rx = max(sea_w + 20, min(width - sea_w - 20, rx))
        # Draw a 12-px wide river ribbon
        for dx in range(-6, 7):
            edge = abs(dx) / 6
            river_c = (int(50 + 30 * edge), int(130 + 30 * edge), int(215 - 20 * edge))
            if 0 <= rx + dx < width:
                s.set_at((rx + dx, y), river_c)

    # ── Thin road line (light grey)
    road_x = int(width * 0.62)
    for y in range(0, height, 1):
        road_x += rng.randint(-1, 1)
        road_x = max(sea_w + 20, min(width - sea_w - 20, road_x))
        if 0 <= road_x < width:
            s.set_at((road_x, y), (190, 185, 170))
            if 0 <= road_x + 1 < width:
                s.set_at((road_x + 1, y), (210, 205, 190))

    # ── Semitransparent cloud puffs
    cloud_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for _ in range(7):
        cx = rng.randint(30, width - 30)
        cy = rng.randint(30, height - 30)
        for _ in range(5):
            ox = rng.randint(-28, 28)
            oy = rng.randint(-10, 10)
            rad = rng.randint(14, 30)
            pygame.draw.circle(cloud_surf, (255, 255, 255, 140), (cx + ox, cy + oy), rad)
    s.blit(cloud_surf, (0, 0))

    return s
