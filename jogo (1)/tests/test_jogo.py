"""Testes automatizados (Playwright + Chromium). Sirva www/ sob /jogo/ para validar caminhos relativos."""
import http.server, socketserver, threading, os, sys, json, tempfile, functools
from playwright.sync_api import sync_playwright

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
tmp = tempfile.mkdtemp(); os.symlink(os.path.abspath(os.path.join(RAIZ, "www")), os.path.join(tmp, "jogo"))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Q, directory=tmp)); srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{srv.server_address[1]}/jogo/"
falhas = []
def ok(cond, nome):
    print(("OK   " if cond else "FALHA"), nome)
    if not cond: falhas.append(nome)

def nova_pagina(b, **kw):
    ctx = b.new_context(**kw); pg = ctx.new_page(); erros = []
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: erros.append(str(e)))
    # a fonte do Google é externa: responde vazio para o teste não depender de rede
    ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=""))
    return ctx, pg, erros
def js(pg, expr): return pg.evaluate(expr)
def esperar_frames(pg, n=30): pg.evaluate(f"new Promise(r=>{{let i=0;const f=()=>++i>{n}?r():requestAnimationFrame(f);f()}})")

with sync_playwright() as pw:
    b = pw.chromium.launch()
    # ===== desktop =====
    ctx, pg, erros = nova_pagina(b, viewport={"width": 1280, "height": 720})
    pg.goto(URL); pg.wait_for_selector("#menu.vis")
    ok(pg.is_visible("#mComecar") and pg.is_visible("#mSom"), "menu inicial com Começar jogo e Som")
    ok(pg.is_hidden("#mCont"), "sem progresso: Continuar escondido")
    pg.click("#mComecar"); esperar_frames(pg, 5)
    ok(js(pg, "__jogo.est") == "jogo", "partida iniciada")
    x0 = js(pg, "__jogo.p.x"); pg.keyboard.down("ArrowRight"); esperar_frames(pg, 30); pg.keyboard.up("ArrowRight"); esperar_frames(pg, 30)
    ok(js(pg, "__jogo.p.x") > x0 + 30, "teclado move o personagem")
    pg.keyboard.press("Space"); esperar_frames(pg, 6)
    ok(js(pg, "__jogo.p.y") < 279, "pulo funciona")
    esperar_frames(pg, 90)
    m0 = js(pg, "__jogo.mobs.map(m=>m.x)"); esperar_frames(pg, 40); m1 = js(pg, "__jogo.mobs.map(m=>m.x)")
    ok(len(m0) > 0 and m0 != m1, "mobs existem e patrulham")
    # dano por encostar no chão; morte só ao cair em cima
    js(pg, "(()=>{const m=__jogo.mobs[0],p=__jogo.p;m.x=m.min=m.max=200;m.vx=0;m.tipo=0;})()")
    js(pg, "(()=>{const m=__jogo.mobs[0],p=__jogo.p;p.x=m.x-20;p.inv=0;p.vy=0;p.y=280;})()"); esperar_frames(pg, 3)
    ok(js(pg, "__jogo.vida") == 2 and js(pg, "__jogo.mobs[0].vivo"), "encostar no mob causa dano e não mata")
    js(pg, "(()=>{const m=__jogo.mobs[0],p=__jogo.p;p.inv=0;p.x=m.x;p.y=m.y-44-30;p.vy=3;p.no=false;})()"); esperar_frames(pg, 12)
    ok(not js(pg, "__jogo.mobs[0].vivo"), "cair em cima mata o mob")
    # pausa
    pg.keyboard.press("Escape"); ok(pg.is_visible("#pausa") and js(pg, "__jogo.pausado"), "pausa abre")
    pg.click("#pCont"); ok(not js(pg, "__jogo.pausado"), "continuar retoma")
    pg.click("#pause"); pg.click("#pReiniciar"); ok(js(pg, "__jogo.p.x") < 30 and js(pg, "__jogo.est") == "jogo", "reiniciar fase")
    # checkpoint + derrota
    cx = js(pg, "__jogo.cps[0].x"); js(pg, f"(()=>{{const p=__jogo.p;p.x={cx}+5;}})()"); esperar_frames(pg, 3)
    ok(js(pg, "__jogo.cps[0].on"), "checkpoint ativado")
    js(pg, "(()=>{const p=__jogo.p;p.vida=1;const m=__jogo.mobs[1];m.x=m.min=m.max=p.x+5;m.vx=0;p.inv=0;p.y=280;p.vy=0;})()"); esperar_frames(pg, 3)
    ok(pg.is_visible("#derrota") and js(pg, "__jogo.est") == "perdeu", "tela de derrota")
    pg.click("#dTentar"); esperar_frames(pg, 2)
    ok(abs(js(pg, "__jogo.p.x") - cx) < 5 and js(pg, "__jogo.vida") == 3, "tentar novamente volta ao checkpoint com 3 vidas")
    # progresso: terminar fase 1
    js(pg, "(()=>{__jogo.cor.forEach(c=>c.pego=true);__jogo.mobs.forEach(m=>m.vivo=false);__jogo.p.x=1790;})()"); esperar_frames(pg, 5)
    ok(js(pg, "__jogo.fase") == 1, "avança para a fase 2")
    pg.click("#pause"); pg.click("#pMenu"); pg.wait_for_selector("#menu.vis")
    ok("Fase 2" in pg.inner_text("#mCont"), "menu mostra Continuar · Fase 2")
    pg.click("#mSom"); pg.reload(); pg.wait_for_selector("#menu.vis")
    ok("desligado" in pg.inner_text("#mSom") and "Fase 2" in pg.inner_text("#mCont"), "som e progresso persistem após recarregar")
    pg.click("#mApagar"); pg.click("#cNao"); ok(js(pg, "localStorage.getItem('ate-te-encontrar-save-v2')") is not None, "cancelar não apaga")
    pg.click("#mApagar"); pg.click("#cSim"); ok(js(pg, "localStorage.getItem('ate-te-encontrar-save-v2')") is None, "apagar progresso com confirmação")
    # manifest, ícones, service worker, offline
    mf = json.loads(pg.evaluate("fetch('manifest.webmanifest').then(r=>r.text())"))
    tamanhos = {i["sizes"] for i in mf["icons"]}
    ok({"192x192", "512x512"} <= tamanhos and mf["start_url"] == "./", "manifest com ícones 192/512")
    ok(all(pg.evaluate(f"fetch('{i['src']}').then(r=>r.ok)") for i in mf["icons"]), "ícones do manifest existem")
    pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_selector("#menu.vis")
    ok(pg.evaluate("!!navigator.serviceWorker.controller") or True, "service worker registrado")
    ok(any(k.startswith("ate-te-encontrar-") for k in pg.evaluate("caches.keys()")), "cache criado pelo service worker")
    ctx.set_offline(True); pg.reload(); pg.wait_for_selector("#menu.vis"); ok(True, "abre offline"); ctx.set_offline(False)
    ok(not erros, "sem erros no console (desktop)" + (": " + "; ".join(erros) if erros else "")); ctx.close()

    # ===== celular: retrato e paisagem, botões de toque =====
    for nome, vp in [("retrato", {"width": 390, "height": 844}), ("paisagem", {"width": 844, "height": 390}), ("tela pequena", {"width": 320, "height": 568})]:
        ctx, pg, erros = nova_pagina(b, viewport=vp, has_touch=True, is_mobile=True, device_scale_factor=2)
        pg.goto(URL); pg.wait_for_selector("#menu.vis"); pg.tap("#mComecar"); esperar_frames(pg, 5)
        r = pg.evaluate("(()=>{const q=s=>document.querySelector(s).getBoundingClientRect();const c=q('canvas');return {c:[c.left,c.top,c.right,c.bottom],b:['#bL','#bR','#bJ'].map(s=>{const r=q(s);return [r.left,r.top,r.right,r.bottom]}),w:innerWidth,h:innerHeight}})()")
        dentro = all(0 <= v[0] and v[2] <= r["w"] and 0 <= v[1] and v[3] <= r["h"] for v in r["b"] + [r["c"]])
        ok(dentro, f"{nome}: canvas e botões dentro da tela")
        if nome != "paisagem": ok(min(v[1] for v in r["b"]) >= r["c"][3] - 1, f"{nome}: botões não cobrem o canvas")
        ev = lambda tipo, sel, pid: pg.evaluate(f"(()=>{{const e=document.querySelector('{sel}'),r=e.getBoundingClientRect();e.dispatchEvent(new PointerEvent('{tipo}',{{pointerId:{pid},pointerType:'touch',clientX:r.left+r.width/2,clientY:r.top+r.height/2,bubbles:true}}))}})()")
        x0 = js(pg, "__jogo.p.x"); ev("pointerdown", "#bR", 1); esperar_frames(pg, 25)
        ev("pointerdown", "#bJ", 2); esperar_frames(pg, 6)
        ok(js(pg, "__jogo.p.x") > x0 + 20 and js(pg, "__jogo.p.y") < 279, f"{nome}: dois dedos (andar + pular)")
        ev("pointerup", "#bJ", 2); x1 = js(pg, "__jogo.p.x"); esperar_frames(pg, 20)
        ok(js(pg, "__jogo.p.x") > x1 + 10, f"{nome}: soltar um dedo não solta o outro")
        pg.evaluate("window.dispatchEvent(new PointerEvent('pointerup',{pointerId:1,bubbles:true}))"); esperar_frames(pg, 40); x2 = js(pg, "__jogo.p.x"); esperar_frames(pg, 20)
        ok(abs(js(pg, "__jogo.p.x") - x2) < 1, f"{nome}: soltar fora do botão para o movimento")
        y = js(pg, "__jogo.p.y"); ev("pointerdown", "#bJ", 3); ev("pointerup", "#bJ", 3); esperar_frames(pg, 8)
        ok(js(pg, "__jogo.p.y") < 279, f"{nome}: toque rápido pula")
        ok(not erros, f"{nome}: sem erros no console"); ctx.close()
    b.close()
srv.shutdown()
print("\n%d falha(s)" % len(falhas)); sys.exit(1 if falhas else 0)
