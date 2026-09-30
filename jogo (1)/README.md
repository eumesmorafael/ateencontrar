# Até te encontrar

Jogo de plataforma romântico feito para navegador e celular (PWA, funciona offline).

## Jogar

https://eumesmorafael.github.io/jogo/

## Como jogar

- **Objetivo de cada fase:** pegue todos os corações 💗 e chegue à seta ➡️ no fim da fase.
- **Inimigos:** pule **em cima** deles (caindo) para derrotá-los. Encostar de lado ou no chão tira uma vida ❤️.
- **Checkpoints 🚩:** ao passar por uma bandeira, se você perder todas as vidas pode "Tentar novamente" dali, sem perder os corações já pegos.
- **Chefe (fase 4):** ele avisa com ❗ antes de investir em linha reta. Pule por cima, ataque com ⚔️ e desvie de novo.
- **Teclado:** ← → (ou A/D) andar · Espaço/↑/W pular (duplo pulo no ar) · X/Z/J atacar (fase do chefe) · Esc/P pausar.
- **Celular:** botões na tela (vários dedos funcionam ao mesmo tempo). Em desktop, use `?controles=1` na URL para ver os botões.

## Instalar no celular

- **Android (Chrome):** abra o link → menu ⋮ → **Instalar app** / **Adicionar à tela inicial**.
- **iPhone (Safari):** botão Compartilhar → **Adicionar à Tela de Início**.

Depois do primeiro carregamento o jogo abre sem internet.

## Rodar localmente

```bash
node scripts/build-www.mjs          # monta a pasta www/
python -m http.server 8000 -d www   # abra http://localhost:8000
```

Edite nome, data e mensagens no topo do `<script>` do `index.html` ("EDITE AQUI"). Fotos e áudios pessoais vão em `fotos/` e `audios/` (copiados para `www/` automaticamente).

## Testes automatizados

```bash
pip install playwright && playwright install chromium
npm test        # monta www/ e roda tests/test_jogo.py
```

Cobrem: menu, partida, teclado, pulo, mobs (patrulha, dano, morte só ao cair em cima), pausa, checkpoint, derrota, salvamento, som, apagar progresso, manifest, ícones, service worker, offline, botões de toque com vários dedos (retrato, paisagem e tela pequena) e ausência de erros no console.

## Apagar o progresso

No menu inicial: **Apagar progresso** (ou **Novo jogo**). Sempre pede confirmação. O progresso nunca é apagado automaticamente (nem ao zerar o jogo).

## Publicar (GitHub Pages)

O workflow `.github/workflows/pages.yml` publica a pasta `www/` a cada push na `main`. Em **Settings → Pages**, deixe **Source = GitHub Actions**. Ao mudar arquivos do jogo, aumente `VERSAO` em `sw.js` para os aparelhos pegarem a versão nova.

## Virar app (Capacitor)

```bash
npm install
npm run cap:add:android   # cria a pasta android/ (uma vez)
npm run cap:sync          # após cada mudança no jogo
npm run cap:open:android  # abre no Android Studio → Build > Build APK
```

Requer Node, JDK 17+ e Android Studio. **iOS exige macOS + Xcode** (`npm i @capacitor/ios && npx cap add ios`) e conta Apple Developer para distribuir. Nenhum APK/IPA está incluído neste repositório.

## Limitações conhecidas

- Testado em Chromium (desktop e emulação de celular). Firefox mobile, Safari/iOS e aparelhos reais ainda precisam de teste manual.
- A fonte Fredoka vem do Google Fonts; offline, cai para uma fonte padrão.
- O som só começa após o primeiro toque/tecla (regra dos navegadores); sem áudio o jogo funciona normalmente.
- Os efeitos sonoros são sintetizados (gerados por script), simples de trocar em `assets/audio/*.wav`.
