// «Сборка» статического сайта: копируем выбранную версию в dist
import { cpSync, rmSync } from 'node:fs';
const src = process.argv[2] || 'app';
rmSync('dist', { recursive: true, force: true });
cpSync(src, 'dist', { recursive: true });
console.log(`built ${src} -> dist`);
