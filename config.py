import os
from pathlib import Path

# Base Data Paths
DATA_ROOT = Path(os.environ.get("ANIME_DATA_DIR", "/data/anime-gallery"))
TEMP_DIR = DATA_ROOT / "temp"
FAVORITES_DIR = DATA_ROOT / "favorites"
CACHE_DIR = DATA_ROOT / "cache"
DB_DIR = DATA_ROOT / "db"

# Ensure all essential directories exist
for d in [DATA_ROOT, TEMP_DIR, FAVORITES_DIR, CACHE_DIR, DB_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "gallery.sqlite3"

# System Defaults
DEFAULT_SEARCH_LIMIT = 100
MAX_SEARCH_LIMIT = 300
THUMBNAIL_SIZE = (800, 1060)  # High-DPI crisp responsive WebP preview
PHASH_SIMILARITY_THRESHOLD = 5  # Hamming distance <= 5 considered duplicate/highly similar

# Server Config
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8088
