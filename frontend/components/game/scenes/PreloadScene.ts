import Phaser from 'phaser';

export class PreloadScene extends Phaser.Scene {
  constructor() {
    super({ key: 'PreloadScene' });
  }

  preload() {
    // Player — 96×96, blue body with light cockpit strip
    const playerGfx = this.make.graphics({ x: 0, y: 0 });
    playerGfx.fillStyle(0x4488ff);
    playerGfx.fillRect(0, 32, 96, 64);
    playerGfx.fillStyle(0xaaccff);
    playerGfx.fillRect(0, 0, 96, 32);
    playerGfx.generateTexture('player', 96, 96);
    playerGfx.destroy();

    // Enemy variants
    const colors = [0xff4444, 0xff8800, 0xcc44ff];
    ['enemy0', 'enemy1', 'enemy2'].forEach((key, i) => {
      const g = this.make.graphics({ x: 0, y: 0 });
      g.fillStyle(colors[i]);
      g.fillRect(0, 0, 84, 84);
      g.generateTexture(key, 84, 84);
      g.destroy();
    });

    // Player bullet — 6×12, cyan
    const pb = this.make.graphics({ x: 0, y: 0 });
    pb.fillStyle(0x00ffff);
    pb.fillRect(0, 0, 6, 12);
    pb.generateTexture('bullet_player', 6, 12);
    pb.destroy();

    // Enemy bullet — 6×10, red
    const eb = this.make.graphics({ x: 0, y: 0 });
    eb.fillStyle(0xff4444);
    eb.fillRect(0, 0, 6, 10);
    eb.generateTexture('bullet_enemy', 6, 10);
    eb.destroy();
  }

  create() {
    this.scene.start('GameScene');
  }
}
