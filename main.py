"""
❤️ My Favorite Person — a Netflix-inspired romantic web app.

Backend: FastAPI. Serves the single-page frontend and an API that
auto-generates cinematic "movie" cards from the photos you drop into
`photos/` or `static/images/`.

Run:
    pip install -r requirements.txt
    python main.py
Then open http://127.0.0.1:8000 on your phone (same Wi-Fi) or PC.
"""

from __future__ import annotations

import os
import random
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# --------------------------------------------------------------------------- #
#  💖  CUSTOMISE ME — everything personal lives here.                          #
# --------------------------------------------------------------------------- #
CONFIG = {
    # Her name — shown on the lock screen, ending credits and greetings.
    "partner_name": "Musku ❤️",
    # The day you met (YYYY-MM-DD). Powers the "Days Since We Met" counter.
    "met_date": "2023-02-14",
    # Optional background music. Drop an mp3 at static/audio/music.mp3
    # (any filename works — the app auto-detects the first audio file).
    "music_hint": "/static/audio/",

    # 🔒 PRIVATE LOCK — she types this to unlock the site. Photos stay hidden
    #    from anyone without it. CHANGE THIS to your own secret (a date, a word…).
    #    On a public host, set the SITE_PASSCODE env var instead of editing here,
    #    so the code isn't visible in your GitHub repo.  Set to "" to disable.
    "passcode": "2696",
    # A gentle hint shown on the lock screen (leave "" for no hint).
    "lock_hint": "You already know it 😉",
}

# Env var wins over the file (keeps the secret out of your repo when deployed).
PASSCODE = (os.environ.get("SITE_PASSCODE") or CONFIG["passcode"] or "").strip()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
IMAGES_DIR = STATIC_DIR / "images"          # future uploads go here
PHOTOS_DIR = BASE_DIR / "photos"            # your existing gallery
AUDIO_DIR = STATIC_DIR / "audio"
TEMPLATES_DIR = BASE_DIR / "templates"

for d in (STATIC_DIR, IMAGES_DIR, AUDIO_DIR, TEMPLATES_DIR):
    d.mkdir(parents=True, exist_ok=True)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".bmp"}
AUDIO_EXTS = {".mp3", ".ogg", ".wav", ".m4a", ".aac"}

# Auto-build the cinematic themed scenes if they're missing (first run).
SCENES_DIR = STATIC_DIR / "scenes"
try:
    if not SCENES_DIR.exists() or not any(SCENES_DIR.glob("*.svg")):
        import generate_scenes
        generate_scenes.generate()
        print("  🎨  Generated cinematic scenes ->", SCENES_DIR)
except Exception as _e:  # scenes are a nice-to-have; never block startup
    print("  ⚠️  Scene generation skipped:", _e)

app = FastAPI(title="My Favorite Person ❤️", docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if PHOTOS_DIR.exists():
    app.mount("/photos", StaticFiles(directory=str(PHOTOS_DIR)), name="photos")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# --------------------------------------------------------------------------- #
#  🔒 Private lock — server-side gate so photos aren't reachable without the   #
#     passcode (not just visually hidden).                                     #
# --------------------------------------------------------------------------- #
import hashlib

COOKIE_NAME = "mfp_access"
_TOKEN = hashlib.sha256(f"my-favorite-person::{PASSCODE}::v1".encode()).hexdigest()[:40]

# Only these paths hold private content; css/js/scenes stay open so the lock
# screen and shell can load.
_GATED_PREFIXES = ("/photos", "/static/images", "/api/catalogue")


def is_unlocked(request: Request) -> bool:
    if not PASSCODE:                       # lock disabled → everything open
        return True
    return request.cookies.get(COOKIE_NAME) == _TOKEN


@app.middleware("http")
async def lock_gate(request: Request, call_next):
    path = request.url.path
    if PASSCODE and path.startswith(_GATED_PREFIXES) and not is_unlocked(request):
        return JSONResponse({"locked": True}, status_code=401)
    return await call_next(request)


# --------------------------------------------------------------------------- #
#  Image discovery                                                            #
# --------------------------------------------------------------------------- #
def _scan(directory: Path, url_prefix: str) -> list[str]:
    if not directory.exists():
        return []
    files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTS
    ]
    files.sort(key=lambda f: f.name.lower())
    return [f"{url_prefix}/{f.name}" for f in files]


def discover_images() -> list[str]:
    """All romantic photos, from both folders. Unlimited images supported."""
    imgs = _scan(PHOTOS_DIR, "/photos") + _scan(IMAGES_DIR, "/static/images")
    return imgs


def discover_audio() -> str | None:
    if not AUDIO_DIR.exists():
        return None
    for f in sorted(AUDIO_DIR.iterdir(), key=lambda f: f.name.lower()):
        if f.is_file() and f.suffix.lower() in AUDIO_EXTS:
            return f"/static/audio/{f.name}"
    return None


# --------------------------------------------------------------------------- #
#  Movie catalogue                                                            #
# --------------------------------------------------------------------------- #
# effect -> gradient + emoji + themed SVG scene (static/scenes/<scene>.svg).
# The scene is the cinematic "world"; your photo is composited into it.
EFFECTS = {
    "Beach":          {"grad": ["#7fd8e8", "#ffe4b5"], "emoji": "🏖️", "scene": "beach"},
    "Ocean":          {"grad": ["#2b3a67", "#f6a35c"], "emoji": "🌊", "scene": "ocean"},
    "Mountains":      {"grad": ["#5b7a96", "#eef6fb"], "emoji": "🏔️", "scene": "mountains"},
    "Snow":           {"grad": ["#c3d4e6", "#5b86b6"], "emoji": "❄️", "scene": "snow"},
    "Aurora":         {"grad": ["#0a1236", "#43e97b"], "emoji": "🌠", "scene": "aurora"},
    "Desert":         {"grad": ["#f4845f", "#7a3b6a"], "emoji": "🏜️", "scene": "desert"},
    "Jungle":         {"grad": ["#1f6b4a", "#8fd66f"], "emoji": "🌴", "scene": "jungle"},
    "Princess Castle":{"grad": ["#ff7eb3", "#8a5cff"], "emoji": "🏰", "scene": "castle"},
    "Royal Queen":    {"grad": ["#c9a227", "#7a0b1e"], "emoji": "👑", "scene": "royal"},
    "Anime Glow":     {"grad": ["#00e5ff", "#ff2bd6"], "emoji": "✨", "scene": "neon"},
    "City Night":     {"grad": ["#1c2b52", "#3a4d7a"], "emoji": "🌃", "scene": "city"},
    "Action":         {"grad": ["#5e1508", "#ff6a2b"], "emoji": "💥", "scene": "action"},
    "Horror":         {"grad": ["#0a0f1e", "#4a5a8a"], "emoji": "🎃", "scene": "horror"},
    "Graveyard":      {"grad": ["#101828", "#2a2140"], "emoji": "👻", "scene": "graveyard"},
    "Fairy Garden":   {"grad": ["#43e97b", "#ff9ad5"], "emoji": "🧚", "scene": "fairy"},
    "Sunset":         {"grad": ["#ff8008", "#e50914"], "emoji": "🌅", "scene": "sunset"},
    "Stars":          {"grad": ["#141e30", "#6a3093"], "emoji": "⭐", "scene": "starrynight"},
    "Galaxy":         {"grad": ["#3a1c71", "#1e3a8a"], "emoji": "🌌", "scene": "galaxy"},
    "Flower Garden":  {"grad": ["#ff9ad5", "#43e97b"], "emoji": "🌸", "scene": "flowers"},
    "Dream Clouds":   {"grad": ["#89f7fe", "#c3ecff"], "emoji": "☁️", "scene": "clouds"},
    "Rain":           {"grad": ["#485563", "#29323c"], "emoji": "🌧️", "scene": "rain"},
    "Love Hearts":    {"grad": ["#e50914", "#ff5e7e"], "emoji": "❤️", "scene": "hearts"},
    "Golden Light":   {"grad": ["#f7971e", "#ffd200"], "emoji": "🌟", "scene": "golden"},
    "Pink Sky":       {"grad": ["#ff9a9e", "#fad0c4"], "emoji": "🌷", "scene": "pinksky"},
    "Magic Sparkles": {"grad": ["#8a2be2", "#ffd700"], "emoji": "🪄", "scene": "sparkles"},
}

CATALOGUE = [
    {
        "title": "Romantic Adventures",
        "movies": [
            ("Beach Vacation", "Beach", ["Romance", "Adventure"],
             "Golden sand, salty air, and your laugh louder than the waves. "
             "Every tide pulls me closer to you — our own little paradise with no return ticket."),
            ("Coffee Date", "Golden Light", ["Romance", "Comedy"],
             "Two cups, one heart. You steal my fries and I let you, because your smile between "
             "sips is the only caffeine I'll ever need."),
            ("Rain Walk", "Rain", ["Romance", "Drama"],
             "One umbrella, two dreamers, and a whole city washed clean. We walked slower just so "
             "the moment — and your hand in mine — would last a little longer."),
            ("Sunset Love", "Sunset", ["Romance", "Adventure"],
             "The sky ran out of colours trying to match how you looked that evening. I stopped "
             "watching the sun the second you looked at me."),
            ("Forever Together", "Love Hearts", ["Romance", "Fantasy"],
             "No plot twists, no cliffhangers — just you and me, renewing our forever every single "
             "day. The only sequel I ever want to make."),
        ],
    },
    {
        "title": "Princess Collection",
        "movies": [
            ("Princess in Pink", "Pink Sky", ["Fantasy", "Romance"],
             "Wrapped in pink and pure magic — my real-life fairytale who doesn't need a crown to "
             "rule every room she walks into."),
            ("Queen of My Heart", "Royal Queen", ["Fantasy", "Drama"],
             "You reign over the softest, most guarded kingdom I own. Long live the queen — she has "
             "my whole heart as her throne."),
            ("Royal Smile", "Golden Light", ["Romance", "Comedy"],
             "One smile from you and the whole kingdom bows. It's illegal to be this radiant, but "
             "I'll happily serve a life sentence."),
            ("Fairytale Date", "Princess Castle", ["Fantasy", "Romance"],
             "Castles, candlelight, and a happily-ever-after we're writing in real time. Every "
             "chapter with you reads better than any storybook."),
            ("My Cinderella", "Magic Sparkles", ["Fantasy", "Romance"],
             "Midnight can strike all it wants — I'd chase you across a hundred kingdoms. You're the "
             "only fit my heart will ever accept."),
        ],
    },
    {
        "title": "Action Heroine",
        "movies": [
            ("Mission: Steal My Heart", "Action", ["Action", "Romance"],
             "Objective: my heart. Status: mission accomplished, no survivors. You didn't just steal "
             "it — you kept it, and I'm not filing a report."),
            ("Spy Love", "City Night", ["Action", "Adventure"],
             "Top secret, high stakes, and one undeniable clue at every scene: I'm hopelessly in "
             "love with the most dangerous agent alive — you."),
            ("Supergirl", "Galaxy", ["Action", "Fantasy"],
             "Faster than my heartbeat, stronger than any bad day. My favourite superpower is the "
             "way you save me just by showing up."),
            ("Wonder Woman", "Anime Glow", ["Action", "Adventure"],
             "Fierce, fearless, unstoppable — and somehow still gentle with me. Wonder isn't your "
             "title, it's what I feel every time I look at you."),
            ("Adventure Queen", "Jungle", ["Adventure", "Comedy"],
             "You turn ordinary Tuesdays into expeditions and grocery runs into quests. Lead the "
             "way, my love — I'm all in, wherever you go."),
        ],
    },
    {
        "title": "Epic Adventures 🏔️",
        "movies": [
            ("Mountain Escape", "Mountains", ["Adventure", "Romance"],
             "Thin air, endless peaks, and you catching your breath at the top — not from the climb, "
             "but because I couldn't stop staring. The whole world below, and I still picked you."),
            ("Snowy Peaks", "Snow", ["Adventure", "Drama"],
             "Cold hands, warmer hearts, one shared scarf. Snowflakes kept landing on your lashes and "
             "I kept forgetting how to speak."),
            ("Northern Lights", "Aurora", ["Fantasy", "Romance"],
             "The sky put on its greatest show and you still out-shone it. Wrapped in a blanket under "
             "the aurora — that's a scene I'll replay forever."),
            ("Desert Dreams", "Desert", ["Adventure", "Fantasy"],
             "Endless golden dunes and one oasis: you. Even in a place made of nothing, being beside "
             "you feels like having everything."),
            ("Ocean Escape", "Ocean", ["Adventure", "Romance"],
             "Salt on our lips, horizon with no end, and a promise as deep as the sea. Sail anywhere "
             "you like, captain — I'm your favourite passenger for life."),
        ],
    },
    {
        "title": "Thrills & Chills 🎃",
        "movies": [
            ("Haunted Date", "Horror", ["Thriller", "Romance"],
             "Spooky night, one flickering candle, and you grabbing my arm at every creak. I'd walk "
             "into any haunted house if it means you hold me that tight."),
            ("Midnight Graveyard", "Graveyard", ["Thriller", "Fantasy"],
             "Full moon, cold mist, and your nervous little laugh echoing between the stones. Scariest "
             "part? How much I love you — it's honestly terrifying."),
            ("Ghostly Love", "Horror", ["Fantasy", "Romance"],
             "In this life or the next, haunting or human — I'd find you every single time. Some "
             "loves refuse to rest, and ours is one of them."),
            ("Vampire Romance", "Graveyard", ["Fantasy", "Thriller"],
             "Forever, immortal, and hopelessly yours. I'd give up a hundred lifetimes for one more "
             "midnight with you. Bite marks optional. 🦇"),
            ("Our Scary Movie Night", "Stars", ["Comedy", "Romance"],
             "You behind a pillow, me pretending I'm not scared, popcorn everywhere. The movie was "
             "forgettable — that cosy, frightened cuddle absolutely was not."),
        ],
    },
    {
        "title": "Cute Moments",
        "movies": [
            ("Funny Faces", "Flower Garden", ["Comedy", "Romance"],
             "The goofy, unguarded, camera-roll faces nobody else gets to see. That silliness is "
             "my favourite kind of beautiful."),
            ("Sleepy Princess", "Dream Clouds", ["Romance", "Comedy"],
             "Half-asleep, fully adorable, mumbling nonsense I'd listen to forever. Watching you "
             "drift off is the softest movie ever made."),
            ("Laugh Attack", "Golden Light", ["Comedy", "Romance"],
             "That laugh you can't control, the one that folds you in half. I'd tell a thousand bad "
             "jokes just to be the reason for it."),
            ("Selfie Queen", "Pink Sky", ["Comedy", "Romance"],
             "A hundred takes and every single one is my new lock screen. The camera loves you — "
             "but not even half as much as I do."),
            ("Food Lover", "Sunset", ["Comedy", "Romance"],
             "You light up over dessert like it's a plot twist. Sharing one plate, two spoons, and "
             "endless 'just one more bite' — my favourite genre."),
        ],
    },
    {
        "title": "Future Dreams",
        "movies": [
            ("Our Wedding", "Love Hearts", ["Romance", "Fantasy"],
             "You in white, me forgetting every word I rehearsed. The best day of a film we haven't "
             "even finished shooting yet — I already know it's a classic."),
            ("Future Home", "Fairy Garden", ["Romance", "Drama"],
             "A little door, warm lights, your laugh echoing down the hall. Home was never a place — "
             "it's wherever you decide to stay."),
            ("World Tour", "Galaxy", ["Adventure", "Romance"],
             "Passports full, hands fuller. Every timezone, every skyline — as long as I'm looking "
             "at it next to you, it's the best view on earth."),
            ("Baby Dreams", "Dream Clouds", ["Romance", "Fantasy"],
             "Tiny shoes, giant dreams, and a future with your eyes and my stubbornness. The sweetest "
             "'coming soon' my heart has ever imagined."),
            ("Growing Old Together", "Snow", ["Romance", "Drama"],
             "Grey hair, same butterflies. Rocking chairs, inside jokes, and a love that only gets "
             "more legendary with every season. Roll credits — slowly."),
        ],
    },
]


def build_catalogue(images: list[str]) -> dict:
    """Attach posters/effects to every movie and auto-generate a gallery row."""
    n = len(images)
    idx = 0
    rating = 5

    categories = []
    for cat in CATALOGUE:
        movies = []
        for (title, effect, genres, desc) in cat["movies"]:
            fx = EFFECTS.get(effect, EFFECTS["Love Hearts"])
            poster = images[idx % n] if n else None
            idx += 1
            movies.append({
                "id": _slug(title),
                "title": title,
                "genres": genres,
                "description": desc,
                "rating": rating,
                "effect": effect,
                "gradient": fx["grad"],
                "emoji": fx["emoji"],
                "scene": f"/static/scenes/{fx['scene']}.svg",
                "poster": poster,
            })
        categories.append({"title": cat["title"], "movies": movies})

    # 🎞️ Auto-generated: one "movie" per photo — unlimited images welcome.
    if n:
        effect_keys = list(EFFECTS.keys())
        auto_movies = []
        for i, img in enumerate(images):
            effect = effect_keys[i % len(effect_keys)]
            fx = EFFECTS[effect]
            auto_movies.append({
                "id": f"memory-{i+1}",
                "title": f"Memory #{i+1}",
                "genres": ["Romance", random.Random(i).choice(
                    ["Fantasy", "Adventure", "Comedy", "Drama"])],
                "description": "A frame I never want to fast-forward. Just you, exactly as you "
                               "were, exactly as I'll always remember you. ❤️",
                "rating": rating,
                "effect": effect,
                "gradient": fx["grad"],
                "emoji": fx["emoji"],
                "scene": f"/static/scenes/{fx['scene']}.svg",
                "poster": img,
            })
        categories.insert(0, {"title": "Made For You ❤️", "movies": auto_movies})

    scenes = [f"/static/scenes/{e['scene']}.svg" for e in EFFECTS.values()]
    return {"categories": categories, "images": images, "scenes": scenes}


def _slug(text: str) -> str:
    keep = "".join(c.lower() if c.isalnum() else "-" for c in text)
    while "--" in keep:
        keep = keep.replace("--", "-")
    return keep.strip("-")


# --------------------------------------------------------------------------- #
#  Routes                                                                     #
# --------------------------------------------------------------------------- #
def _og(request: Request) -> dict:
    """Absolute link-preview data (works behind Render's HTTPS proxy)."""
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("host", request.url.netloc)
    base = f"{proto}://{host}"
    return {
        "title": f"My Favorite Person, {CONFIG['partner_name']}",
        "desc": "A private love story — made just for you. 💌",
        "image": f"{base}/static/preview.png",
        "url": f"{base}/",
    }


@app.get("/manifest.webmanifest")
async def manifest():
    """Home-screen install name/icon (Android 'Add to Home screen')."""
    return JSONResponse({
        "name": f"My Favorite Person, {CONFIG['partner_name']}",
        "short_name": CONFIG["partner_name"],
        "start_url": "/",
        "display": "standalone",
        "background_color": "#141414",
        "theme_color": "#141414",
        "icons": [
            {"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png",
             "purpose": "any maskable"},
        ],
    }, media_type="application/manifest+json")


@app.get("/")
async def home(request: Request):
    # Locked? Show the romantic unlock screen instead of the app.
    if not is_unlocked(request):
        return templates.TemplateResponse(
            "lock.html",
            {"request": request,
             "hint": CONFIG.get("lock_hint", ""),
             "partner": CONFIG["partner_name"],
             "og": _og(request)},
        )
    images = discover_images()
    client_config = {
        "partnerName": CONFIG["partner_name"],
        "metDate": CONFIG["met_date"],
        "music": discover_audio(),
        "imageCount": len(images),
    }
    return templates.TemplateResponse(
        "index.html", {"request": request, "config": client_config, "og": _og(request)}
    )


@app.post("/unlock")
async def unlock(request: Request):
    """Check the passcode; on success set a year-long access cookie."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    code = str(body.get("code", "")).strip()
    if PASSCODE and code == PASSCODE:
        resp = JSONResponse({"ok": True})
        resp.set_cookie(
            COOKIE_NAME, _TOKEN,
            max_age=60 * 60 * 24 * 365, httponly=True, samesite="lax",
            secure=(request.url.scheme == "https"),
        )
        return resp
    return JSONResponse({"ok": False}, status_code=401)


@app.get("/lock")
async def relock():
    """Sign out (clears the access cookie)."""
    resp = JSONResponse({"ok": True})
    resp.delete_cookie(COOKIE_NAME)
    return resp


@app.get("/api/catalogue")
async def api_catalogue():
    images = discover_images()
    data = build_catalogue(images)
    data["music"] = discover_audio()
    data["hasImages"] = bool(images)
    return JSONResponse(data)


@app.get("/api/health")
async def health():
    return {"status": "ok", "images": len(discover_images())}


if __name__ == "__main__":
    import uvicorn

    # Cloud hosts (Render, Railway, Fly, Heroku…) inject the port via $PORT.
    port = int(os.environ.get("PORT", "8000"))
    print("\n  ❤️  My Favorite Person is starting...")
    print("  📷  Photos found:", len(discover_images()))
    print(f"  🌐  Open on this PC:      http://127.0.0.1:{port}")
    print(f"  📱  Open on your phone:   http://<your-pc-ip>:{port}  (same Wi-Fi)\n")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
