import sqlite3
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, List, Optional
from datetime import datetime
from config import DB_PATH, DATA_ROOT

LOGS_DIR = DATA_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("anime_gallery.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. 角色表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        avatar_url TEXT,
        current_page INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_searched_at TIMESTAMP,
        total_candidates INTEGER DEFAULT 0,
        total_favorites INTEGER DEFAULT 0
    )
    """)

    try:
        cursor.execute("ALTER TABLE characters ADD COLUMN current_page INTEGER DEFAULT 1")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE characters ADD COLUMN game TEXT DEFAULT 'other'")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE characters ADD COLUMN aliases TEXT")
    except sqlite3.OperationalError: pass

    # 2. 图片表 (含 Google Photos 预留字段)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
        filename TEXT NOT NULL,
        temp_path TEXT,
        favorites_path TEXT,
        thumbnail_path TEXT,
        original_source TEXT,
        source_url TEXT,
        source_id TEXT,
        author_name TEXT,
        author_url TEXT,
        title TEXT,
        copyright_info TEXT,
        width INTEGER DEFAULT 0,
        height INTEGER DEFAULT 0,
        file_size INTEGER DEFAULT 0,
        phash TEXT,
        dhash TEXT,
        ahash TEXT,
        status TEXT DEFAULT 'pending', -- pending, saved, deleted, cleaned
        rating TEXT DEFAULT 'sfw', -- sfw (全年龄), r18 (R-18)
        google_sync_status TEXT DEFAULT 'not_synced', -- not_synced, synced, failed (Google Photos 扩展预留)
        google_photo_id TEXT,
        download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        saved_time TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 动态检查/增加字段（若已有旧表）
    try:
        cursor.execute("ALTER TABLE images ADD COLUMN rating TEXT DEFAULT 'sfw'")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE images ADD COLUMN google_sync_status TEXT DEFAULT 'not_synced'")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE images ADD COLUMN google_photo_id TEXT")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE images ADD COLUMN batch_number INTEGER DEFAULT 1")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE images ADD COLUMN task_id TEXT")
    except sqlite3.OperationalError: pass
    cursor.execute("UPDATE images SET batch_number = 1 WHERE batch_number IS NULL OR batch_number = 0")

    # 3. 任务表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        character_name TEXT NOT NULL,
        character_id INTEGER,
        rating TEXT DEFAULT 'sfw', -- sfw (全年龄), r18 (R-18)
        status TEXT DEFAULT 'queued', -- queued, searching, downloading, processing, completed, paused, failed, cancelled
        progress_current INTEGER DEFAULT 0,
        progress_total INTEGER DEFAULT 100,
        progress_message TEXT,
        result_count INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN rating TEXT DEFAULT 'sfw'")
    except sqlite3.OperationalError: pass

    # 4. 全局设置表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        description TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 索引优化
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_char_status ON images(character_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_images_phash ON images(phash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at DESC)")

    # 5. 授权设备与会话凭证表 (Device Authorization & Token Table)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS authorized_devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE NOT NULL,
        device_name TEXT NOT NULL,
        ip_address TEXT,
        user_agent TEXT,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_auth_token ON authorized_devices(token)")

    # 初始默认设置
    default_settings = [
        ("private_auth_enabled", "true", "启用个人设备私有独占防护模式 (仅授权设备可访问)"),
        ("private_access_key", "aurora888", "个人设备专属访问密钥/PIN密码 (用于在手机和电脑初次配对授权)"),
        ("max_search_limit", "100", "每次角色搜索最大获取候选图片数量"),
        ("default_crawl_rating", "sfw", "默认抓取图片属性 (sfw: 全年龄, r18: R-18)"),
        ("max_disk_usage_percent", "85", "磁盘空间警报阈值百分比"),
        ("pixiv_refresh_token", "", "Pixiv 官方用户授权 OAuth Refresh Token"),
        ("safebooru_enabled", "true", "启用 Safebooru 公开 API 数据源"),
        ("danbooru_enabled", "true", "启用 Danbooru 公开 API 数据源"),
        ("gelbooru_enabled", "true", "启用 Gelbooru 公开 API 数据源"),
        ("zerochan_enabled", "true", "启用 Zerochan 官方数据源"),
        ("google_photos_sync_enabled", "false", "Google Photos 自动同步开关"),
        ("google_photos_client_id", "", "Google Photos OAuth Client ID"),
        ("google_photos_client_secret", "", "Google Photos OAuth Client Secret"),
        ("google_photos_refresh_token", "", "Google Photos OAuth Refresh Token"),
        ("google_photos_album_name", "Anime Gallery Favorites", "Google Photos 目标相册名称")
    ]
    for k, v, desc in default_settings:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)", (k, v, desc))

    conn.commit()
    seed_characters(conn)
    conn.close()
    logger.info("Database initialized successfully.")

def seed_characters(conn=None):
    """
    Seed or update predefined characters from CHARACTER_CATALOG for
    Blue Archive, Wuthering Waves, and Arknights: Endfield.
    """
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        from services.character_catalog import CHARACTER_CATALOG
    except Exception as e:
        logger.warning(f"Could not import CHARACTER_CATALOG: {e}")
        return

    cursor = conn.cursor()
    for item in CHARACTER_CATALOG:
        name = item["name"]
        slug = item["slug"]
        game = item["game"]
        aliases_json = json.dumps(item.get("aliases", []), ensure_ascii=False)
        default_avatar = f"/static/avatars/{slug}.svg"

        existing = cursor.execute("SELECT id, avatar_url, game, aliases FROM characters WHERE name = ?", (name,)).fetchone()
        if existing:
            cur_avatar = existing["avatar_url"]
            if not cur_avatar or cur_avatar.endswith(".svg"):
                new_avatar = default_avatar
            else:
                new_avatar = cur_avatar

            cursor.execute("""
                UPDATE characters 
                SET slug = ?, game = ?, aliases = ?, avatar_url = ?
                WHERE id = ?
            """, (slug, game, aliases_json, new_avatar, existing["id"]))
        else:
            cursor.execute("""
                INSERT OR IGNORE INTO characters (name, slug, game, aliases, avatar_url, current_page)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (name, slug, game, aliases_json, default_avatar))

    conn.commit()
    if close_after:
        conn.close()
    logger.info("Character seed completed successfully.")

if __name__ == "__main__":
    init_db()
