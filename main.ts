// Copies the image beside this file to /output/entry.png, as the bounty asks.
import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const OUT = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const HERE = dirname(fileURLToPath(import.meta.url));

mkdirSync(OUT, { recursive: true });
copyFileSync(join(HERE, 'entry.png'), join(OUT, 'entry.png'));