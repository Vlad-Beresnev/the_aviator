import Phaser from 'phaser';
import {
  FPS,
  LEVEL_DURATION,
  MAX_BATTERY,
  ENEMY_BASE_SPEED,
  ENEMY_BASE_SPAWN_INTERVAL,
  ENEMY_BASE_FIRE_INTERVAL,
  DIFFICULTY_SCALE_STEP,
  LEVEL_SCALE_STEP,
  MAX_LEVEL_SCALE_BONUS,
  IN_LEVEL_RAMP_MAX,
  PLAYER_SPEED,
  PLAYER_FIRE_INTERVAL,
  BULLET_SPEED,
  ENEMY_BULLET_SPEED,
  HIT_DAMAGE,
} from '../constants';

const BAR_W = 175;
const BAR_H = 20;
const BAR_Y = 10;
const BAR_X = 10;
const BAR_GAP = 8;

export class GameScene extends Phaser.Scene {
  private player!: Phaser.GameObjects.Image;
  private enemies: Phaser.GameObjects.Image[] = [];
  private playerBullets: Phaser.GameObjects.Image[] = [];
  private enemyBullets: Phaser.GameObjects.Image[] = [];

  private currentBattery = MAX_BATTERY;
  private frame = 0;
  private spawnTimer = 0;
  private fireCooldown = 0;
  private difficulty = 1;
  private level = 1;
  private onComplete!: (r: { victory: boolean; battery: number }) => void;
  private gameOver = false;

  private bgTile!: Phaser.GameObjects.TileSprite;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private wasdKeys!: { W: Phaser.Input.Keyboard.Key; A: Phaser.Input.Keyboard.Key; S: Phaser.Input.Keyboard.Key; D: Phaser.Input.Keyboard.Key };
  private spaceKey!: Phaser.Input.Keyboard.Key;

  private batteryBarFill!: Phaser.GameObjects.Rectangle;
  private timerBarFill!: Phaser.GameObjects.Rectangle;
  private kmBarBg!: Phaser.GameObjects.Rectangle;
  private kmBarFill!: Phaser.GameObjects.Rectangle;
  private kmText!: Phaser.GameObjects.Text;
  private timerBarBg!: Phaser.GameObjects.Rectangle;
  private batteryBarBg!: Phaser.GameObjects.Rectangle;

  constructor() {
    super({ key: 'GameScene' });
  }

  init() {
    this.difficulty = this.registry.get('difficulty') ?? 1;
    this.level = this.registry.get('level') ?? 1;
    this.currentBattery = this.registry.get('battery') ?? MAX_BATTERY;
    this.onComplete = this.registry.get('onComplete');
    this.frame = 0;
    this.spawnTimer = 0;
    this.fireCooldown = 0;
    this.gameOver = false;
    this.enemies = [];
    this.playerBullets = [];
    this.enemyBullets = [];
  }

  create() {
    this.createBackground();

    // Player
    this.player = this.add.image(this.gameWidth / 2, this.gameHeight - 60, 'player');

    this.scale.on('resize', this.handleResize, this);
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.scale.off('resize', this.handleResize, this);
    });

    // Input
    this.cursors = this.input.keyboard!.createCursorKeys();
    this.wasdKeys = {
      W: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      A: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      S: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      D: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    };
    this.spaceKey = this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

    // HUD
    this.buildHUD();
  }

  private get gameWidth() {
    return this.scale.width;
  }

  private get gameHeight() {
    return this.scale.height;
  }

  private createBackground() {
    const width = Math.max(1, this.gameWidth);
    const height = Math.max(1, this.gameHeight);

    if (this.bgTile) {
      this.bgTile.setPosition(width / 2, height / 2);
      this.bgTile.setSize(width, height);
      return;
    }

    const bgGfx = this.make.graphics({ x: 0, y: 0 });
    bgGfx.fillStyle(0x0a0a1a);
    bgGfx.fillRect(0, 0, width, height);
    bgGfx.fillStyle(0xffffff);
    for (let i = 0; i < 120; i++) {
      const sx = Phaser.Math.Between(0, width - 1);
      const sy = Phaser.Math.Between(0, height - 1);
      const sw = Phaser.Math.Between(1, 3);
      bgGfx.fillRect(sx, sy, sw, sw);
    }
    bgGfx.generateTexture('bg', width, height);
    bgGfx.destroy();

    this.bgTile = this.add.tileSprite(width / 2, height / 2, width, height, 'bg');
  }

  private buildHUD() {
    const sideBarW = this.getSideBarWidth();
    const kmBarX = BAR_X + sideBarW + BAR_GAP;
    const kmBarW = this.getKmBarWidth();

    // Battery bar (left)
    this.batteryBarBg = this.add.rectangle(BAR_X, BAR_Y, sideBarW, BAR_H, 0x333333).setOrigin(0, 0);
    this.batteryBarFill = this.add.rectangle(BAR_X, BAR_Y, sideBarW, BAR_H, 0x00c850).setOrigin(0, 0);

    // KM bar (center)
    this.kmBarBg = this.add.rectangle(kmBarX, BAR_Y, kmBarW, BAR_H, 0x333333).setOrigin(0, 0);
    this.kmBarFill = this.add.rectangle(kmBarX, BAR_Y, kmBarW, BAR_H, 0x4488ff).setOrigin(0, 0);
    this.kmText = this.add.text(
      kmBarX + kmBarW / 2,
      BAR_Y + BAR_H / 2,
      '450 KM',
      { fontSize: '13px', color: '#ffffff' }
    ).setOrigin(0.5, 0.5);

    // Timer bar (right)
    const timerX = this.gameWidth - BAR_X - sideBarW;
    this.timerBarBg = this.add.rectangle(timerX, BAR_Y, sideBarW, BAR_H, 0x333333).setOrigin(0, 0);
    this.timerBarFill = this.add.rectangle(timerX, BAR_Y, sideBarW, BAR_H, 0x50a0ff).setOrigin(0, 0);
  }

  private getSideBarWidth() {
    const available = Math.max(0, this.gameWidth - BAR_X * 2 - BAR_GAP * 2);
    return Math.min(BAR_W, Math.max(72, Math.floor(available * 0.28)));
  }

  private getKmBarWidth() {
    const sideBarW = this.getSideBarWidth();
    return Math.max(60, this.gameWidth - BAR_X * 2 - BAR_GAP * 2 - sideBarW * 2);
  }

  private handleResize() {
    this.createBackground();
    this.player.x = Phaser.Math.Clamp(this.player.x, 48, this.gameWidth - 48);
    this.player.y = Phaser.Math.Clamp(this.player.y, 48, this.gameHeight - 48);

    const sideBarW = this.getSideBarWidth();
    const kmBarX = BAR_X + sideBarW + BAR_GAP;
    const kmBarW = this.getKmBarWidth();
    const timerX = this.gameWidth - BAR_X - sideBarW;

    this.batteryBarBg.setSize(sideBarW, BAR_H);
    this.batteryBarFill.setSize(sideBarW, BAR_H);
    this.kmBarBg.setPosition(kmBarX, BAR_Y).setSize(kmBarW, BAR_H);
    this.kmBarFill.setPosition(kmBarX, BAR_Y).setSize(kmBarW, BAR_H);
    this.kmText.setPosition(kmBarX + kmBarW / 2, BAR_Y + BAR_H / 2);
    this.timerBarBg.setPosition(timerX, BAR_Y).setSize(sideBarW, BAR_H);
    this.timerBarFill.setPosition(timerX, BAR_Y).setSize(sideBarW, BAR_H);
  }

  update(_time: number, delta: number) {
    if (this.gameOver) return;

    const dt = delta / (1000 / FPS);
    const durationFrames = LEVEL_DURATION * FPS;
    const progress = this.frame / durationFrames;

    // Difficulty ramp
    const levelBonus = Math.min((this.level - 1) * LEVEL_SCALE_STEP, MAX_LEVEL_SCALE_BONUS);
    const scale = 1.0 + (this.difficulty - 1) * DIFFICULTY_SCALE_STEP + levelBonus;
    const baseEnemySpeed = ENEMY_BASE_SPEED * (0.8 + scale * 0.4);
    const baseSpawnInterval = Math.max(10, Math.floor(ENEMY_BASE_SPAWN_INTERVAL / scale));
    const ramp = 1.0 + progress * IN_LEVEL_RAMP_MAX;
    const enemySpeed = baseEnemySpeed * ramp;
    const spawnInterval = Math.max(8, Math.floor(baseSpawnInterval / ramp));
    const fireInterval = Math.max(
      12,
      Math.floor(Math.max(15, Math.floor(ENEMY_BASE_FIRE_INTERVAL / scale)) / ramp)
    );

    // Player movement
    const left = this.cursors.left.isDown || this.wasdKeys.A.isDown;
    const right = this.cursors.right.isDown || this.wasdKeys.D.isDown;
    const up = this.cursors.up.isDown || this.wasdKeys.W.isDown;
    const down = this.cursors.down.isDown || this.wasdKeys.S.isDown;
    if (left) this.player.x -= PLAYER_SPEED * dt;
    if (right) this.player.x += PLAYER_SPEED * dt;
    if (up) this.player.y -= PLAYER_SPEED * dt;
    if (down) this.player.y += PLAYER_SPEED * dt;
    this.player.x = Phaser.Math.Clamp(this.player.x, 48, this.gameWidth - 48);
    this.player.y = Phaser.Math.Clamp(this.player.y, 48, this.gameHeight - 48);

    // Player firing
    this.fireCooldown = Math.max(0, this.fireCooldown - dt);
    if (this.fireCooldown <= 0 && this.spaceKey.isDown) {
      const b = this.add.image(this.player.x, this.player.y - 48, 'bullet_player');
      b.setData('dy', -BULLET_SPEED);
      this.playerBullets.push(b);
      this.fireCooldown = PLAYER_FIRE_INTERVAL;
    }

    // Enemy spawning
    this.spawnTimer += dt;
    if (this.spawnTimer >= spawnInterval) {
      this.spawnTimer = 0;
      const ex = Phaser.Math.Between(20, this.gameWidth - 20);
      const variant = Phaser.Math.Between(0, 2);
      const e = this.add.image(ex, -42, `enemy${variant}`);
      e.setData('speed', enemySpeed + Phaser.Math.FloatBetween(-0.5, 0.5));
      e.setData('drift', Phaser.Math.FloatBetween(-1.5, 1.5));
      e.setData('fireTimer', Phaser.Math.Between(0, fireInterval));
      e.setData('fireInterval', fireInterval);
      this.enemies.push(e);
    }

    // Update enemies + enemy firing
    const nextEnemies: Phaser.GameObjects.Image[] = [];
    for (const e of this.enemies) {
      e.y += e.getData('speed') * dt;
      e.x += e.getData('drift') * dt;
      if (e.x < 0 || e.x > this.gameWidth) e.setData('drift', -e.getData('drift'));
      const ft: number = e.getData('fireTimer') - dt;
      e.setData('fireTimer', ft);
      if (ft <= 0) {
        const b = this.add.image(e.x, e.y + 42, 'bullet_enemy');
        b.setData('dy', ENEMY_BULLET_SPEED);
        this.enemyBullets.push(b);
        e.setData('fireTimer', fireInterval + Phaser.Math.Between(-10, 10));
      }
      if (e.y < this.gameHeight + 20) nextEnemies.push(e);
      else e.destroy();
    }
    this.enemies = nextEnemies;

    // Move bullets
    for (const b of this.playerBullets) b.y += b.getData('dy') * dt;
    for (const b of this.enemyBullets) b.y += b.getData('dy') * dt;

    // Cull out-of-bounds bullets
    this.playerBullets = this.playerBullets.filter(b => {
      if (b.y < -10) { b.destroy(); return false; }
      return true;
    });
    this.enemyBullets = this.enemyBullets.filter(b => {
      if (b.y > this.gameHeight + 10) { b.destroy(); return false; }
      return true;
    });

    // Collision: player bullets vs enemies
    const playerR = new Phaser.Geom.Rectangle(this.player.x - 40, this.player.y - 40, 80, 80);
    const hitEnemyIdxs = new Set<number>();
    const hitBulletIdxs = new Set<number>();
    for (let ei = 0; ei < this.enemies.length; ei++) {
      const e = this.enemies[ei];
      const er = new Phaser.Geom.Rectangle(e.x - 42, e.y - 42, 84, 84);
      for (let bi = 0; bi < this.playerBullets.length; bi++) {
        const b = this.playerBullets[bi];
        const br = new Phaser.Geom.Rectangle(b.x - 3, b.y - 6, 6, 12);
        if (Phaser.Geom.Intersects.RectangleToRectangle(er, br)) {
          hitEnemyIdxs.add(ei);
          hitBulletIdxs.add(bi);
        }
      }
    }
    this.enemies = this.enemies.filter((e, i) => {
      if (hitEnemyIdxs.has(i)) { e.destroy(); return false; }
      return true;
    });
    this.playerBullets = this.playerBullets.filter((b, i) => {
      if (hitBulletIdxs.has(i)) { b.destroy(); return false; }
      return true;
    });

    // Collision: enemy bullets vs player
    const hitEnemyBullets: Phaser.GameObjects.Image[] = [];
    for (const b of this.enemyBullets) {
      const br = new Phaser.Geom.Rectangle(b.x - 3, b.y - 5, 6, 10);
      if (Phaser.Geom.Intersects.RectangleToRectangle(playerR, br)) {
        this.currentBattery -= HIT_DAMAGE;
        hitEnemyBullets.push(b);
        if (this.currentBattery <= 0) {
          b.destroy();
          this.enemyBullets = this.enemyBullets.filter(x => !hitEnemyBullets.includes(x));
          this.triggerLose();
          return;
        }
      }
    }
    for (const b of hitEnemyBullets) b.destroy();
    this.enemyBullets = this.enemyBullets.filter(b => !hitEnemyBullets.includes(b));

    // Collision: enemy bodies vs player
    const hitEnemies: Phaser.GameObjects.Image[] = [];
    for (const e of this.enemies) {
      const er = new Phaser.Geom.Rectangle(e.x - 42, e.y - 42, 84, 84);
      if (Phaser.Geom.Intersects.RectangleToRectangle(playerR, er)) {
        this.currentBattery -= HIT_DAMAGE * 2;
        hitEnemies.push(e);
        if (this.currentBattery <= 0) {
          e.destroy();
          this.enemies = this.enemies.filter(x => !hitEnemies.includes(x));
          this.triggerLose();
          return;
        }
      }
    }
    for (const e of hitEnemies) e.destroy();
    this.enemies = this.enemies.filter(e => !hitEnemies.includes(e));

    // Passive battery drain: 33% of MAX_BATTERY over LEVEL_DURATION
    const passiveDrainPerFrame = (0.33 * MAX_BATTERY) / (LEVEL_DURATION * FPS);
    this.currentBattery = Math.max(0, this.currentBattery - passiveDrainPerFrame * dt);

    // Scroll background
    this.bgTile.tilePositionY -= 1 * dt;

    // HUD update
    this.updateHUD(progress);

    // Frame counter + win check
    this.frame += dt;
    if (this.frame >= durationFrames) {
      this.triggerWin();
    }
  }

  private updateHUD(progress: number) {
    const batRatio = Math.max(0, this.currentBattery / MAX_BATTERY);
    const durationFrames = LEVEL_DURATION * FPS;
    const timeRatio = Math.max(0, 1 - this.frame / durationFrames);
    const kmRatio = timeRatio;

    const sideBarW = this.getSideBarWidth();
    const kmBarW = this.getKmBarWidth();

    // Battery bar
    this.batteryBarFill.width = sideBarW * batRatio;
    const batColor = batRatio > 0.4 ? 0x00c850 : batRatio > 0.15 ? 0xffb400 : 0xdc2828;
    this.batteryBarFill.fillColor = batColor;

    // Timer bar
    this.timerBarFill.width = sideBarW * timeRatio;
    this.timerBarFill.fillColor = timeRatio > 0.3 ? 0x50a0ff : 0xff7800;

    // KM bar + text
    this.kmBarFill.width = kmBarW * kmRatio;
    const kmLeft = Math.round(450 * kmRatio);
    this.kmText.setText(`${kmLeft} KM`);

    void progress;
  }

  private triggerWin() {
    this.gameOver = true;
    const cb = this.registry.get('onComplete') as (r: { victory: boolean; battery: number }) => void;
    cb({ victory: true, battery: Math.round(this.currentBattery) });
  }

  private triggerLose() {
    this.gameOver = true;
    const cb = this.registry.get('onComplete') as (r: { victory: boolean; battery: number }) => void;
    cb({ victory: false, battery: 0 });
  }
}
