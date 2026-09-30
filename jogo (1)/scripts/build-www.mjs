// Copia só os arquivos do jogo para ./www (usado pelo GitHub Pages e pelo Capacitor).
import { cpSync, rmSync, mkdirSync, existsSync } from "node:fs";
rmSync("www", { recursive: true, force: true }); mkdirSync("www");
["index.html", "manifest.webmanifest", "sw.js", "404.html", "assets", "fotos", "audios"].forEach(f => { if (existsSync(f)) cpSync(f, `www/${f}`, { recursive: true }); });
console.log("www/ pronto");
