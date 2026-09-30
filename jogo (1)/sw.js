// Mude VERSAO a cada publicação para que os aparelhos baixem os arquivos novos.
const VERSAO = "2.1.0";
const CACHE = "ate-te-encontrar-" + VERSAO;
const ARQUIVOS = [
  "./", "./index.html", "./manifest.webmanifest",
  "./assets/eu.png", "./assets/ela.png", "./assets/icon-192.png", "./assets/icon-512.png",
  "./assets/icon-maskable-512.png", "./assets/apple-touch-icon.png",
  ...["pulo", "coracao", "dano", "mob", "ataque", "chefe", "vitoria"].map(n => `./assets/audio/${n}.wav`)
];

self.addEventListener("install", event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await Promise.all(ARQUIVOS.map(async url => {
      const res = await fetch(new Request(url, { cache: "reload" }));
      if (!res.ok) throw new Error("Falha ao baixar " + url); // não guarda arquivo quebrado
      await cache.put(url, res);
    }));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const chaves = await caches.keys();
    await Promise.all(chaves.filter(k => k.startsWith("ate-te-encontrar-") && k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

async function guardar(request, res) {
  if (res && res.ok && res.type === "basic") { const c = await caches.open(CACHE); await c.put(request, res.clone()); }
  return res;
}

self.addEventListener("fetch", event => {
  const req = event.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== self.location.origin || req.headers.has("range")) return;
  if (req.mode === "navigate") { // páginas: rede primeiro (pega versão nova), cache se offline
    event.respondWith(fetch(req).then(r => guardar(req, r)).catch(async () => (await caches.match(req)) || (await caches.match("./index.html"))));
    return;
  }
  event.respondWith((async () => { // arquivos: cache primeiro
    const hit = await caches.match(req);
    if (hit) return hit;
    try { return await guardar(req, await fetch(req)); } catch (e) { return Response.error(); }
  })());
});
