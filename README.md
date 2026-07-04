# ❤️ My Favorite Person

A premium, **Netflix-inspired romantic web app** where she is the main character in
every movie. Built with **FastAPI** (Python) + **HTML / CSS / vanilla JS**.
Mobile-first and tuned for **Android Chrome**.

---

## 🚀 Run it

```bash
pip install -r requirements.txt
python main.py
```

Then open:

- On this PC → **http://127.0.0.1:8000**
- On your phone (same Wi-Fi) → **http://YOUR-PC-IP:8000**
  (find your IP with `ipconfig` — use the IPv4 address, e.g. `192.168.1.5`)

Stop the server with `Ctrl + C`.

---

## 📷 Your photos

The app **automatically builds movie cards from your photos** — unlimited images supported.

- Existing photos in the **`photos/`** folder are used automatically (22 detected 🎉).
- You can also drop more images into **`static/images/`**.
- Supported: `.jpg .jpeg .png .webp .gif .avif .bmp`

Every photo becomes a card in the **“Made For You ❤️”** row, and all photos appear
in each movie's **Watch Memory** cinematic slideshow (ken burns, zoom, pan, floating hearts…).
Just add or remove images and **refresh** — no code changes needed.

---

## 🎵 Background music (optional)

Drop any audio file into **`static/audio/`** (e.g. `static/audio/song.mp3`).
The app auto-detects it. Tap the 🎵 button to play/mute.
Supported: `.mp3 .ogg .wav .m4a .aac`

---

## 💝 Make it personal

Open **`main.py`** and edit the `CONFIG` block at the top:

```python
CONFIG = {
    "partner_name": "My Love ❤️",   # shown in the ending credits
    "met_date": "2023-02-14",       # powers the "Days Since We Met" counter
}
```

The special message text lives in `static/js/app.js` (search for `const MESSAGE`).

---

## 🔒 Private passcode lock

The site is locked — she types a secret code to get in, and the photos are
**blocked server-side** for anyone who doesn't have it (not just hidden).

Set your code in `main.py` → `CONFIG["passcode"]` (default `0214`) and the hint in
`CONFIG["lock_hint"]`. To turn the lock off, set `"passcode": ""`.

> **When deploying to a public host, don't put the real code in the repo.**
> Leave `passcode` as-is (or blank) and instead set an environment variable
> **`SITE_PASSCODE`** on the host — it overrides the file, so the secret never
> touches GitHub. Keeping the repo **private** is also a good idea.

Access lasts a year per device; visiting `/lock` signs out.

---

## ☁️ Deploy it online (so she can open it from anywhere)

Already deploy-ready — includes `Procfile`, `Dockerfile`, `render.yaml`, `runtime.txt`,
and the server reads `$PORT`. Photos, scenes and the song are committed, so they ship
with the app.

**Easiest — Render.com (free):**
1. Push this folder to a **GitHub** repo (private recommended).
2. On [render.com](https://render.com) → **New → Blueprint** → pick the repo (it reads `render.yaml`).
3. In the service's **Environment**, add `SITE_PASSCODE` = your secret code.
4. Deploy → you get a public `https://…onrender.com` link to send her. 💌

Also works on Railway, Fly.io, or any Docker host (use the included `Dockerfile`).
Note: free tiers may “sleep” when idle and take ~30s to wake on the first visit.

---

## ✨ Features

- Netflix-style loading screen, navbar, hero banner & horizontal movie rows
- 5 themed categories + auto-generated “Made For You” row from your photos
- Cinematic movie detail pages → **Watch Memory** animated slideshow
- Fade / zoom / pan / ken-burns / tilt transitions + floating hearts
- Animated **Love Meter** (999999% · Forever Loading…)
- Typewriter **Special Message** popup
- **Secret Ending**: confetti + fireworks + hearts → rolling **Ending Credits**
- “Days Since We Met” live counter · random love quotes
- Background music toggle · snow toggle · ambient particles · heart cursor/touch trail
- Private romantic passcode lock (server-enforced)
- Fully responsive, touch-swipe, no horizontal scroll, lazy-loaded images
- Android-Chrome tuned: notch/gesture-bar safe areas, no long-press image menus,
  address-bar-proof heights, battery-saving FX pause during playback
- Easter egg: tap the ❤️ logo 5× 😉

Made with ❤️ · Directed by Love · Produced by Destiny
