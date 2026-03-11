import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_difficulty_scaling_increases():
    """Higher level + difficulty should produce faster enemies and shorter spawn intervals."""
    import config
    results = []
    for level, difficulty in [(1, 1), (5, 3), (10, 5)]:
        scale = 1.0 + (difficulty - 1) * 0.25 + (level - 1) * 0.08
        enemy_speed = config.ENEMY_BASE_SPEED * (0.8 + scale * 0.4)
        spawn_interval = max(10, int(config.ENEMY_BASE_SPAWN_INTERVAL / scale))
        fire_interval = max(15, int(config.ENEMY_BASE_FIRE_INTERVAL / scale))
        results.append((enemy_speed, spawn_interval, fire_interval))

    # Speed should increase with level
    assert results[0][0] < results[1][0] < results[2][0]
    # Spawn interval should decrease (more enemies)
    assert results[0][1] > results[1][1] > results[2][1]
    # Fire interval should decrease (more shots)
    assert results[0][2] > results[1][2] > results[2][2]


def test_config_constants_valid():
    """Game config constants have sane values."""
    import config
    assert config.GAME_WIDTH > 0
    assert config.GAME_HEIGHT > 0
    assert config.LEVEL_DURATION > 0
    assert config.FPS > 0
    assert config.ENEMY_BASE_SPEED > 0
    assert config.ENEMY_BASE_SPAWN_INTERVAL > 0
    assert config.ENEMY_BASE_FIRE_INTERVAL > 0
    assert config.PLAYER_SPEED > 0
    assert config.BULLET_SPEED > 0
    assert config.ENEMY_BULLET_SPEED > 0
    assert config.HIT_DAMAGE > 0
    assert config.RELOAD_COST > 0
    assert config.INITIAL_LEVELS > 0


def test_sprites_importable():
    """sprites module is importable (pygame must be installed)."""
    import sprites
    assert hasattr(sprites, "make_player")
    assert hasattr(sprites, "make_enemy")
    assert hasattr(sprites, "make_bullet_player")
    assert hasattr(sprites, "make_bullet_enemy")
    assert hasattr(sprites, "make_explosion_frames")
    assert hasattr(sprites, "make_background")
