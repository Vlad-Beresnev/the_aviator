'use client';

import { useEffect, useRef } from 'react';

interface PhaserGameProps {
  difficulty: number;
  level: number;
  battery: number;
  onComplete: (result: { victory: boolean; battery: number }) => void;
}

export default function PhaserGame({ difficulty, level, battery, onComplete }: PhaserGameProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const gameRef = useRef<import('phaser').Game | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    let cancelled = false;

    const initGame = async () => {
      const Phaser = (await import('phaser')).default;
      const { PreloadScene } = await import('./scenes/PreloadScene');
      const { GameScene } = await import('./scenes/GameScene');

      if (cancelled || !containerRef.current) return;

      gameRef.current?.destroy(true);
      containerRef.current.replaceChildren();

      const game = new Phaser.Game({
        type: Phaser.AUTO,
        width: window.innerWidth,
        height: window.innerHeight,
        parent: containerRef.current!,
        backgroundColor: '#0a0a1a',
        scene: [PreloadScene, GameScene],
        scale: {
          mode: Phaser.Scale.RESIZE,
          parent: containerRef.current,
          width: '100%',
          height: '100%',
        },
        physics: {
          default: 'arcade',
          arcade: { gravity: { x: 0, y: 0 } },
        },
      });

      game.registry.set('difficulty', difficulty);
      game.registry.set('level', level);
      game.registry.set('battery', battery);
      game.registry.set('onComplete', onComplete);

      if (cancelled) {
        game.destroy(true);
        return;
      }

      gameRef.current = game;
    };

    initGame();

    return () => {
      cancelled = true;
      gameRef.current?.destroy(true);
      gameRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        position: 'fixed',
        inset: 0,
        width: '100vw',
        height: '100vh',
        overflow: 'hidden',
        background: '#0a0a1a',
      }}
    />
  );
}
