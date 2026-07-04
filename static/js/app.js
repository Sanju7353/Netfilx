/* ============================================================
   ❤️  My Favorite Person — app.js
   Vanilla JS · touch-first · optimized for Android Chrome
   ============================================================ */
'use strict';

const CFG = window.APP_CONFIG || {};
const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

/* ---- state ---- */
const State = {
  images: [],
  scenes: [],         // themed SVG worlds
  catalogue: [],
  moviesById: {},
  current: null,      // current movie in detail/player
  slides: [],         // her photo urls for the current player
  sceneOrder: [],     // themed worlds cycled through the slideshow
  slideIdx: 0,
  playing: false,
  timer: null,
  musicOn: false,
  snowOn: false,
};

const LOVE_QUOTES = [
  "You are my favorite notification. ❤️",
  "Every love story is beautiful, but ours is my favorite.",
  "I found my forever the day I found you.",
  "You're the plot twist I never saw coming and never want to end.",
  "Home is not a place. Home is you.",
  "In a world of reruns, you're my favorite original.",
  "Loving you is my favorite thing to binge.",
  "You + Me = the only sequel I'll ever need.",
  "My heart buffers a little every time you smile.",
  "You're the reason I believe in happily ever afters.",
];

/* ============================================================
   BOOT
   ============================================================ */
document.addEventListener('DOMContentLoaded', init);

async function init() {
  startLoader();
  wireGlobalEvents();
  startCountdown();
  rotateHeroQuote();
  buildParticles();
  buildCelebrateCanvas();
  buildSnow();
  setupMusic();

  try {
    const res = await fetch('/api/catalogue');
    if (res.status === 401) { location.replace('/'); return; }  // session lapsed → lock screen
    const data = await res.json();
    State.catalogue = data.categories || [];
    State.images = data.images || [];
    State.scenes = data.scenes || [];
    indexMovies();
    renderRows();
    setHeroBackground();
  } catch (e) {
    console.error('catalogue load failed', e);
    renderEmptyState();
  }

  // Reveal after a short cinematic beat
  setTimeout(hideLoader, 2100);
  observeReveal();
}

/* ============================================================
   LOADER
   ============================================================ */
function startLoader() { document.body.style.overflow = 'hidden'; }
function hideLoader() {
  const l = $('#loader');
  if (!l) return;
  l.classList.add('hide');
  document.body.style.overflow = '';
  toast('Welcome to your love story ❤️');
}

/* ============================================================
   DATA
   ============================================================ */
function indexMovies() {
  State.moviesById = {};
  State.catalogue.forEach(cat =>
    cat.movies.forEach(m => { State.moviesById[m.id] = m; }));
}

function gradientCss(m) {
  const g = m.gradient || ['#e50914', '#ff5e7e'];
  return `linear-gradient(135deg, ${g[0]}, ${g[1]})`;
}

/* ============================================================
   RENDER ROWS
   ============================================================ */
function renderRows() {
  const wrap = $('#rows');
  wrap.innerHTML = '';
  State.catalogue.forEach((cat, ci) => {
    const row = document.createElement('section');
    row.className = 'row';
    if (ci === 0) row.id = 'memories';
    if (cat.title.toLowerCase().includes('made for you')) row.id = 'gallery';

    const head = document.createElement('div');
    head.className = 'row-head';
    head.innerHTML =
      `<h2 class="row-title">${cat.title}</h2><span class="row-more">Swipe ›</span>`;
    row.appendChild(head);

    const track = document.createElement('div');
    track.className = 'row-track';
    cat.movies.forEach((m, i) => track.appendChild(makeCard(m, i)));
    row.appendChild(track);
    wrap.appendChild(row);
  });
  // Anchor for "Our Memories" if not set
  if (!$('#memories')) State.catalogue.length && ($('.row').id = 'memories');
}

function makeCard(m, i) {
  const card = document.createElement('div');
  card.className = 'card';
  card.style.animationDelay = Math.min(i * 55, 480) + 'ms';
  const genres = (m.genres || []).join(' · ');
  const sceneBg = m.scene ? `background-image:url('${m.scene}')` : `background:${gradientCss(m)}`;

  // Her photo sits framed inside the themed world; falls back to the emoji.
  const portrait = m.poster
    ? `<span class="card-starring">STARRING</span>
       <img class="card-portrait" loading="lazy" decoding="async" src="${m.poster}"
            alt="${m.title}" onerror="this.style.display='none'">`
    : `<div class="card-fallback">${m.emoji}</div>`;

  card.innerHTML = `
    <div class="card-scene" style="${sceneBg}"></div>
    ${portrait}
    <div class="card-scrim"></div>
    <span class="card-tag">MY ❤️</span>
    <span class="card-fx">${m.emoji}</span>
    <div class="card-info">
      <div class="card-title">${m.title}</div>
      <div class="card-sub"><span class="rating-inline">★★★★★</span> ${genres}</div>
    </div>`;
  card.addEventListener('click', () => openDetail(m.id));
  return card;
}

function renderEmptyState() {
  $('#rows').innerHTML =
    `<div style="text-align:center;padding:60px 20px;color:#b3b3b3">
       <div style="font-size:60px">📷❤️</div>
       <p style="margin-top:14px;font-size:16px">Drop photos into the <b>photos/</b> folder<br>and refresh to see your movies.</p>
     </div>`;
}

/* ============================================================
   HERO
   ============================================================ */
function setHeroBackground() {
  const bg = $('#heroBg');
  if (State.images.length) {
    let i = 0;
    const apply = () => { bg.style.backgroundImage =
      `linear-gradient(135deg,rgba(20,20,20,.2),rgba(20,20,20,.2)), url("${State.images[i]}")`; };
    apply();
    setInterval(() => { i = (i + 1) % State.images.length; apply(); }, 7000);
  }
}

function rotateHeroQuote() {
  const el = $('#heroQuote');
  let i = 0;
  const show = () => {
    el.style.opacity = 0;
    setTimeout(() => {
      el.textContent = '“' + LOVE_QUOTES[i % LOVE_QUOTES.length] + '”';
      el.style.transition = 'opacity .6s';
      el.style.opacity = 1;
      i++;
    }, 400);
  };
  show();
  setInterval(show, 5200);
}

/* ============================================================
   COUNTDOWN
   ============================================================ */
function startCountdown() {
  const el = $('#daysCounter');
  const met = new Date((CFG.metDate || '2023-01-01') + 'T00:00:00');
  const tick = () => {
    const days = Math.max(0, Math.floor((Date.now() - met.getTime()) / 86400000));
    animateNumber(el, days);
  };
  tick();
}
function animateNumber(el, target) {
  const dur = 1400, start = performance.now();
  const step = now => {
    const p = Math.min(1, (now - start) / dur);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.floor(eased * target).toLocaleString();
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ============================================================
   DETAIL PAGE
   ============================================================ */
function openDetail(id) {
  const m = State.moviesById[id];
  if (!m) return;
  State.current = m;
  $('#detailTitle').textContent = m.title;
  $('#detailDesc').textContent = m.description;
  $('#detailRating').textContent = '★★★★★';
  $('#detailGenres').textContent = (m.genres || []).join(' · ');
  const bg = $('#detailBg');
  // themed world as the cinematic backdrop; her photo framed in front
  bg.style.backgroundImage = m.scene ? `url("${m.scene}")` : gradientCss(m);
  const portrait = $('#detailPortrait');
  if (m.poster) { portrait.src = m.poster; portrait.style.display = ''; }
  else { portrait.removeAttribute('src'); portrait.style.display = 'none'; }
  const d = $('#detail');
  d.classList.add('open');
  d.setAttribute('aria-hidden', 'false');
  d.scrollTop = 0;
  document.body.style.overflow = 'hidden';
  spawnHearts(6);
}
function closeDetail() {
  const d = $('#detail');
  d.classList.remove('open');
  d.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

/* ============================================================
   SLIDESHOW PLAYER
   ============================================================ */
const SCENE_FX = ['fx-kenburns', 'fx-zoomin', 'fx-zoomout', 'fx-panleft', 'fx-panright', 'fx-tilt'];
const PHOTO_FX = ['pfx-rise', 'pfx-zoom', 'pfx-float', 'pfx-tilt', 'pfx-sway'];
const SLIDE_MS = 5200;

function openPlayer() {
  const m = State.current;
  if (!m) return;
  // Her photos — shuffled, with this movie's cover first for context.
  let pics = State.images.slice();
  pics = seededShuffle(pics, hashStr(m.id));
  if (m.poster) { pics = [m.poster, ...pics.filter(p => p !== m.poster)]; }
  State.slides = pics;
  // Themed worlds — start with this movie's own scene, then cycle the rest,
  // so each photo of her appears inside a different environment.
  let sc = (State.scenes || []).slice();
  sc = [m.scene, ...seededShuffle(sc.filter(s => s !== m.scene), hashStr(m.id) + 3)];
  State.sceneOrder = sc.filter(Boolean);
  State.slideIdx = 0;

  $('#playerTitle').textContent = m.title;
  const stage = $('#playerStage');
  stage.innerHTML = '';
  // Pre-create two slide layers we cross-fade between
  stage.appendChild(makeSlideEl());
  stage.appendChild(makeSlideEl());

  const p = $('#player');
  p.classList.add('open');
  p.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  State.playing = true;
  $('#playPauseBtn').textContent = '⏸';
  showSlide(0, true);
  startHeartRain();
}
function makeSlideEl() {
  const s = document.createElement('div');
  s.className = 'slide';
  s.innerHTML = `<div class="slide-scene"></div><img class="slide-photo" alt="">`;
  return s;
}
function closePlayer() {
  const p = $('#player');
  p.classList.remove('open');
  p.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = 'hidden'; // detail still open underneath
  clearTimeout(State.timer);
  State.playing = false;
  stopHeartRain();
  if (!$('#detail').classList.contains('open')) document.body.style.overflow = '';
}

function showSlide(idx) {
  const m = State.current;
  const nP = State.slides.length;
  const nS = State.sceneOrder.length;
  clearTimeout(State.timer);
  const layers = $$('.slide', $('#playerStage'));
  const incoming = layers.find(l => !l.classList.contains('show')) || layers[0];
  const outgoing = layers.find(l => l.classList.contains('show'));

  const i = ((idx % (nP || 1)) + (nP || 1)) % (nP || 1);
  const herUrl = nP ? State.slides[i] : null;
  const sceneUrl = nS ? State.sceneOrder[((idx % nS) + nS) % nS] : m.scene;

  const scene = incoming.querySelector('.slide-scene');
  const photo = incoming.querySelector('.slide-photo');

  // reset animations, then force reflow so they replay
  scene.className = 'slide-scene';
  photo.className = 'slide-photo';
  void incoming.offsetWidth;

  const sfx = SCENE_FX[((idx % SCENE_FX.length) + SCENE_FX.length) % SCENE_FX.length];
  const pfx = PHOTO_FX[((idx % PHOTO_FX.length) + PHOTO_FX.length) % PHOTO_FX.length];

  scene.style.backgroundImage = sceneUrl ? `url("${sceneUrl}")` : gradientCss(m);
  scene.classList.add(sfx);

  let fb = incoming.querySelector('.slide-fallback');
  if (herUrl) {
    if (fb) { fb.remove(); }
    photo.style.display = '';
    photo.src = herUrl;
    photo.classList.add(pfx);
  } else {
    photo.style.display = 'none';
    if (!fb) { fb = document.createElement('div'); fb.className = 'slide-fallback'; incoming.appendChild(fb); }
    fb.textContent = m.emoji;
  }

  requestAnimationFrame(() => incoming.classList.add('show'));
  if (outgoing && outgoing !== incoming) {
    setTimeout(() => outgoing.classList.remove('show'), 900);
  }

  State.slideIdx = i;
  updateCaption();
  updateProgress();

  if (State.playing) State.timer = setTimeout(nextSlide, SLIDE_MS);
}
function updateCaption() {
  const cap = $('#playerCaption');
  cap.classList.remove('show');
  const line = State.current.title.toUpperCase() +
    (State.slides.length ? `  ·  ${State.slideIdx + 1}/${State.slides.length}` : '');
  const romantic = [
    '❤️ My favorite person', 'Every frame, forever', 'You, and only you',
    'My happiest chapter', 'Replaying this one always', 'Screenshotting my heart',
  ];
  setTimeout(() => {
    cap.textContent = romantic[State.slideIdx % romantic.length];
    cap.classList.add('show');
  }, 300);
}
function updateProgress() {
  const n = State.slides.length || 1;
  $('#playerProgress').style.width = ((State.slideIdx + 1) / n * 100) + '%';
}
function nextSlide() { showSlide(State.slideIdx + 1); }
function prevSlide() { showSlide(State.slideIdx - 1); }
function togglePlay() {
  State.playing = !State.playing;
  $('#playPauseBtn').textContent = State.playing ? '⏸' : '▶';
  if (State.playing) State.timer = setTimeout(nextSlide, 2500);
  else clearTimeout(State.timer);
}
function shuffleSlides() {
  State.slides = seededShuffle(State.slides, (State.slideIdx + 7) * 131);
  State.slideIdx = 0;
  showSlide(0, true);
  toast('Shuffled ❤️');
}

/* ============================================================
   SPECIAL MESSAGE (typewriter)
   ============================================================ */
const MESSAGE =
`I'm sorry if I made you upset.

You are my favorite notification.
My safest place.
My happiest chapter.
And my forever person.

Can we restart today's episode together? ❤️`;

let typeTimer = null;
function openMessage() {
  const modal = $('#messageModal');
  modal.classList.add('open');
  modal.setAttribute('aria-hidden', 'false');
  const el = $('#typedMessage');
  el.innerHTML = '';
  clearTimeout(typeTimer);
  let i = 0;
  const cursor = '<span class="cursor">&nbsp;</span>';
  const type = () => {
    el.innerHTML = MESSAGE.slice(0, i).replace(/\n/g, '<br>') + cursor;
    i++;
    if (i <= MESSAGE.length) typeTimer = setTimeout(type, i < 20 ? 55 : 34);
    else el.innerHTML = MESSAGE.replace(/\n/g, '<br>') + cursor;
  };
  type();
}
function closeMessage() {
  const modal = $('#messageModal');
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  clearTimeout(typeTimer);
}

/* ============================================================
   SECRET ENDING → celebration → credits
   ============================================================ */
function openSecret() {
  closeMessage();
  toast("I'd choose you in every universe. 🎆");
  celebrate();
  spawnHearts(40);
  banner("I'd choose you in every universe.");
  setTimeout(openCredits, 4200);
}
function banner(text) {
  const b = document.createElement('div');
  b.textContent = text;
  b.style.cssText =
    `position:fixed;inset:0;z-index:905;display:grid;place-items:center;text-align:center;
     font-size:clamp(24px,7vw,46px);font-weight:900;color:#fff;padding:24px;pointer-events:none;
     text-shadow:0 0 40px rgba(229,9,20,.8);opacity:0;transition:opacity .8s;`;
  document.body.appendChild(b);
  requestAnimationFrame(() => (b.style.opacity = 1));
  setTimeout(() => { b.style.opacity = 0; setTimeout(() => b.remove(), 900); }, 3600);
}

/* Ending credits */
function openCredits() {
  $('#crStar').textContent = (CFG.partnerName || 'Her ❤️');
  const c = $('#credits');
  c.classList.add('open');
  c.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  requestAnimationFrame(() => c.classList.add('rolling'));
}
function closeCredits() {
  const c = $('#credits');
  c.classList.remove('open', 'rolling');
  c.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

/* ============================================================
   MUSIC
   ============================================================ */
function setupMusic() {
  const audio = $('#bgAudio');
  if (CFG.music) audio.src = CFG.music;
  const btn = $('#musicBtn');
  btn.addEventListener('click', () => {
    if (!CFG.music) { toast('🎵 Add a song to static/audio/ to enable music'); return; }
    if (State.musicOn) {
      audio.pause(); State.musicOn = false; btn.classList.remove('active');
    } else {
      audio.play().then(() => {
        State.musicOn = true; btn.classList.add('active'); toast('🎵 Playing our song');
      }).catch(() => toast('Tap again to allow audio 🎵'));
    }
  });
}

/* ============================================================
   SNOW TOGGLE
   ============================================================ */
let snowRAF = null, snowFlakes = [];
function buildSnow() {
  const cv = $('#snow'), ctx = cv.getContext('2d');
  const resize = () => { cv.width = innerWidth; cv.height = innerHeight; };
  resize(); addEventListener('resize', resize);
  const make = () => Array.from({ length: 90 }, () => ({
    x: Math.random() * cv.width, y: Math.random() * cv.height,
    r: Math.random() * 3 + 1, s: Math.random() * 1 + .4, w: Math.random() * .6,
  }));
  snowFlakes = make();
  const draw = () => {
    ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.fillStyle = 'rgba(255,255,255,.85)';
    snowFlakes.forEach(f => {
      ctx.beginPath(); ctx.arc(f.x, f.y, f.r, 0, 7); ctx.fill();
      f.y += f.s; f.x += Math.sin(f.y * .01) * f.w;
      if (f.y > cv.height) { f.y = -5; f.x = Math.random() * cv.width; }
    });
    snowRAF = requestAnimationFrame(draw);
  };
  window._snowDraw = draw;
}
function toggleSnow() {
  const cv = $('#snow'), btn = $('#snowBtn');
  State.snowOn = !State.snowOn;
  if (State.snowOn) {
    cv.style.display = 'block'; btn.classList.add('active');
    window._snowDraw(); toast('❄️ Let it snow');
  } else {
    cv.style.display = 'none'; btn.classList.remove('active');
    cancelAnimationFrame(snowRAF);
  }
}

/* ============================================================
   AMBIENT PARTICLES (floating hearts + sparkles)
   ============================================================ */
function buildParticles() {
  const cv = $('#particles'), ctx = cv.getContext('2d');
  const resize = () => { cv.width = innerWidth; cv.height = innerHeight; };
  resize(); addEventListener('resize', resize);
  const N = innerWidth < 600 ? 14 : 26;
  const parts = Array.from({ length: N }, () => spawnParticle(cv));
  let cleared = false;
  const draw = () => {
    // Pause ambient hearts while a fullscreen scene plays or the tab is hidden
    // (keeps her phone cool & the slideshow buttery). RAF keeps ticking cheaply.
    if (fxPaused()) {
      if (!cleared) { ctx.clearRect(0, 0, cv.width, cv.height); cleared = true; }
      return requestAnimationFrame(draw);
    }
    cleared = false;
    ctx.clearRect(0, 0, cv.width, cv.height);
    parts.forEach(p => {
      p.y -= p.s; p.x += Math.sin(p.y * .01 + p.seed) * .4; p.rot += p.rs;
      if (p.y < -30) Object.assign(p, spawnParticle(cv), { y: cv.height + 20 });
      ctx.save();
      ctx.globalAlpha = p.a;
      ctx.translate(p.x, p.y); ctx.rotate(p.rot);
      ctx.font = p.size + 'px serif';
      ctx.fillText(p.char, 0, 0);
      ctx.restore();
    });
    requestAnimationFrame(draw);
  };
  draw();
}
function spawnParticle(cv) {
  const chars = ['❤', '💗', '✨', '❤', '💕', '⭐'];
  return {
    x: Math.random() * cv.width, y: Math.random() * cv.height,
    s: Math.random() * .5 + .2, size: Math.random() * 14 + 10,
    a: Math.random() * .35 + .1, seed: Math.random() * 6,
    char: chars[(Math.random() * chars.length) | 0],
    rot: Math.random() * 6, rs: (Math.random() - .5) * .02,
  };
}

/* ============================================================
   CELEBRATION CANVAS (confetti + fireworks + hearts)
   ============================================================ */
let CEL;
function buildCelebrateCanvas() {
  const cv = $('#celebrate');
  const ctx = cv.getContext('2d');
  const resize = () => { cv.width = innerWidth; cv.height = innerHeight; };
  resize(); addEventListener('resize', resize);
  CEL = { cv, ctx, parts: [], running: false };
}
function celebrate() {
  const { cv } = CEL;
  const colors = ['#E50914', '#ff5e7e', '#ffd54a', '#ffffff', '#ff9ad5', '#46d369'];
  // confetti burst
  for (let i = 0; i < 160; i++) {
    CEL.parts.push({
      x: Math.random() * cv.width, y: -20 - Math.random() * cv.height * .3,
      vx: (Math.random() - .5) * 4, vy: Math.random() * 3 + 2,
      g: .08, size: Math.random() * 8 + 4, rot: Math.random() * 6, rs: (Math.random() - .5) * .3,
      color: colors[(Math.random() * colors.length) | 0], type: 'confetti', life: 260,
    });
  }
  // fireworks
  let fw = 0;
  const shoot = () => {
    if (fw++ > 5) return;
    fireworkBurst(Math.random() * cv.width, Math.random() * cv.height * .5 + 60, colors);
    setTimeout(shoot, 550);
  };
  shoot();
  // floating hearts
  for (let i = 0; i < 40; i++) {
    CEL.parts.push({
      x: Math.random() * cv.width, y: cv.height + Math.random() * 100,
      vx: (Math.random() - .5) * 1.2, vy: -(Math.random() * 2 + 1.2),
      g: 0, size: Math.random() * 20 + 14, rot: 0, rs: (Math.random() - .5) * .05,
      color: colors[(Math.random() * 2) | 0], type: 'heart', life: 300, a: 1,
    });
  }
  if (!CEL.running) { CEL.running = true; celLoop(); }
}
function fireworkBurst(x, y, colors) {
  const c = colors[(Math.random() * colors.length) | 0];
  for (let i = 0; i < 46; i++) {
    const ang = (Math.PI * 2 * i) / 46, sp = Math.random() * 3 + 2;
    CEL.parts.push({
      x, y, vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp,
      g: .04, size: 3, rot: 0, rs: 0, color: c, type: 'spark', life: 90, a: 1,
    });
  }
}
function celLoop() {
  const { ctx, cv } = CEL;
  ctx.clearRect(0, 0, cv.width, cv.height);
  CEL.parts.forEach(p => {
    p.vy += p.g; p.x += p.vx; p.y += p.vy; p.rot += p.rs; p.life--;
    if (p.a !== undefined && p.life < 60) p.a = Math.max(0, p.life / 60);
    ctx.save();
    ctx.globalAlpha = p.a !== undefined ? p.a : 1;
    ctx.translate(p.x, p.y); ctx.rotate(p.rot);
    ctx.fillStyle = p.color;
    if (p.type === 'heart') { ctx.font = p.size + 'px serif'; ctx.fillText('❤', 0, 0); }
    else if (p.type === 'spark') { ctx.beginPath(); ctx.arc(0, 0, p.size, 0, 7); ctx.fill(); }
    else { ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * .6); }
    ctx.restore();
  });
  CEL.parts = CEL.parts.filter(p => p.life > 0 && p.y < cv.height + 40);
  if (CEL.parts.length) requestAnimationFrame(celLoop);
  else { CEL.running = false; ctx.clearRect(0, 0, cv.width, cv.height); }
}

/* Small heart pops (touch / detail open) */
function spawnHearts(count) {
  for (let i = 0; i < count; i++) {
    setTimeout(() => {
      const h = document.createElement('div');
      h.textContent = ['❤', '💗', '💕', '✨'][(Math.random() * 4) | 0];
      const x = Math.random() * innerWidth;
      h.style.cssText =
        `position:fixed;left:${x}px;top:${innerHeight}px;z-index:940;font-size:${14 + Math.random() * 20}px;
         pointer-events:none;color:#ff5e7e;filter:drop-shadow(0 0 6px rgba(229,9,20,.5));
         transition:transform 2.6s ease-out,opacity 2.6s;`;
      document.body.appendChild(h);
      requestAnimationFrame(() => {
        h.style.transform = `translate(${(Math.random() - .5) * 120}px,-${innerHeight + 60}px) rotate(${(Math.random() - .5) * 90}deg)`;
        h.style.opacity = 0;
      });
      setTimeout(() => h.remove(), 2700);
    }, i * 45);
  }
}

/* Continuous heart rain during slideshow */
let heartRainTimer = null;
function startHeartRain() { stopHeartRain(); heartRainTimer = setInterval(() => spawnHearts(2), 700); }
function stopHeartRain() { clearInterval(heartRainTimer); }

/* ============================================================
   HEART CURSOR / TOUCH TRAIL
   ============================================================ */
function setupCursor() {
  const c = $('#heartCursor');
  if (matchMedia('(hover:hover)').matches) {
    let vis = false;
    addEventListener('mousemove', e => {
      c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px';
      if (!vis) { c.style.opacity = 1; vis = true; }
    });
  }
  // touch trail on mobile
  addEventListener('touchstart', e => {
    const t = e.touches[0];
    if (t) touchHeart(t.clientX, t.clientY);
  }, { passive: true });
}
function touchHeart(x, y) {
  const h = document.createElement('div');
  h.textContent = '❤';
  h.style.cssText =
    `position:fixed;left:${x}px;top:${y}px;z-index:945;color:#E50914;font-size:20px;
     pointer-events:none;transform:translate(-50%,-50%);transition:transform .9s,opacity .9s;`;
  document.body.appendChild(h);
  requestAnimationFrame(() => { h.style.transform = 'translate(-50%,-140%) scale(1.8)'; h.style.opacity = 0; });
  setTimeout(() => h.remove(), 950);
}

/* ============================================================
   GLOBAL EVENTS / DELEGATION
   ============================================================ */
function wireGlobalEvents() {
  setupCursor();

  // navbar scroll
  addEventListener('scroll', () => {
    $('#navbar').classList.toggle('scrolled', scrollY > 30);
  }, { passive: true });

  // mobile menu
  $('#menuBtn').addEventListener('click', () => $('#navLinks').classList.toggle('open'));
  $$('#navLinks a').forEach(a => a.addEventListener('click', () => $('#navLinks').classList.remove('open')));

  // snow
  $('#snowBtn').addEventListener('click', toggleSnow);

  // action delegation
  document.addEventListener('click', e => {
    const el = e.target.closest('[data-action]');
    if (!el) return;
    const act = el.dataset.action;
    ({
      continue: () => { if (State.catalogue[0]?.movies[0]) openDetail(State.catalogue[0].movies[0].id); },
      mylist:   () => { spawnHearts(12); toast('Added to My List ❤️ (it was always you)'); },
      message:  openMessage,
      closeMessage,
      secret:   openSecret,
      closeDetail,
      watch:    openPlayer,
      likeMovie:() => { spawnHearts(14); toast(`❤️ ${State.current?.title} — my favorite`); },
      closePlayer,
      prevSlide, nextSlide, togglePlay, shuffleSlides,
      closeCredits,
    }[act])?.();
  });

  // swipe on player
  setupSwipe();

  // keyboard
  addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      if ($('#player').classList.contains('open')) return closePlayer();
      if ($('#credits').classList.contains('open')) return closeCredits();
      if ($('#messageModal').classList.contains('open')) return closeMessage();
      if ($('#detail').classList.contains('open')) return closeDetail();
    }
    if ($('#player').classList.contains('open')) {
      if (e.key === 'ArrowRight') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
      if (e.key === ' ') { e.preventDefault(); togglePlay(); }
    }
  });

  // easter egg: tap brand 5x
  let brandTaps = 0, brandT;
  $('.brand').addEventListener('click', e => {
    e.preventDefault();
    brandTaps++; clearTimeout(brandT);
    brandT = setTimeout(() => (brandTaps = 0), 900);
    if (brandTaps >= 5) { brandTaps = 0; openSecret(); }
    else scrollTo({ top: 0, behavior: 'smooth' });
  });

  // double-tap a slide to zoom + heart
  $('#playerStage').addEventListener('dblclick', () => { spawnHearts(10); toast('❤️'); });
}

/* ---- swipe ---- */
function setupSwipe() {
  const stage = $('#player');
  let x0 = null, y0 = null, t0 = 0;
  stage.addEventListener('touchstart', e => {
    x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; t0 = Date.now();
  }, { passive: true });
  stage.addEventListener('touchend', e => {
    if (x0 == null) return;
    const dx = e.changedTouches[0].clientX - x0;
    const dy = e.changedTouches[0].clientY - y0;
    const dt = Date.now() - t0;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) && dt < 700) {
      dx < 0 ? nextSlide() : prevSlide();
    } else if (dy > 90 && Math.abs(dy) > Math.abs(dx)) {
      closePlayer();
    }
    x0 = y0 = null;
  }, { passive: true });
}

/* ============================================================
   REVEAL ON SCROLL
   ============================================================ */
function observeReveal() {
  const meter = $('#meterFill');
  if (!meter) return;
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) { meter.style.width = '100%'; io.disconnect(); }
    });
  }, { threshold: .3 });
  io.observe($('.love-meter'));
}

/* ============================================================
   UTILITIES
   ============================================================ */
function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._t);
  t._t = setTimeout(() => t.classList.remove('show'), 2600);
}
// Ambient FX pause while a fullscreen scene is up or the tab is backgrounded
function fxPaused() {
  return document.hidden ||
    $('#player').classList.contains('open') ||
    $('#credits').classList.contains('open');
}
function hashStr(s) { let h = 0; for (const c of String(s)) h = (h * 31 + c.charCodeAt(0)) | 0; return Math.abs(h); }
function seededShuffle(arr, seed) {
  const a = arr.slice(); let s = seed || 1;
  const rand = () => { s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; };
  for (let i = a.length - 1; i > 0; i--) { const j = (rand() * (i + 1)) | 0;[a[i], a[j]] = [a[j], a[i]]; }
  return a;
}
