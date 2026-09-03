import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import TEMP_DIR, FAVORITES_DIR, CACHE_DIR, DATA_ROOT
from database import get_connection

logger = logging.getLogger("anime_gallery.services.storage")

class StorageService:
    @staticmethod
    def get_character_temp_dir(character_name: str) -> Path:
        p = TEMP_DIR / character_name.strip()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def get_character_favorites_dir(character_name: str) -> Path:
        p = FAVORITES_DIR / character_name.strip()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def get_character_cache_dir(character_name: str) -> Path:
        p = CACHE_DIR / character_name.strip()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def save_favorite_image(image_id: int) -> bool:
        """
        Copies candidate image from temp/ to favorites/ and updates DB status to 'saved'.
        """
        conn = get_connection()
        img = conn.execute("""
            SELECT i.*, c.name as character_name 
            FROM images i 
            JOIN characters c ON i.character_id = c.id 
            WHERE i.id = ?
        """, (image_id,)).fetchone()

        if not img:
            conn.close()
            return False

        char_name = img["character_name"]
        filename = img["filename"]

        temp_file = Path(img["temp_path"]) if img["temp_path"] else StorageService.get_character_temp_dir(char_name) / filename
        fav_dir = StorageService.get_character_favorites_dir(char_name)
        fav_file = fav_dir / filename

        # Copy file to favorites
        if temp_file.exists() and not fav_file.exists():
            shutil.copy2(str(temp_file), str(fav_file))

        # Update DB record
        conn.execute("""
            UPDATE images 
            SET status = 'saved', favorites_path = ?, saved_time = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (str(fav_file), image_id))

        # Update character total favorites
        conn.execute("""
            UPDATE characters 
            SET total_favorites = (SELECT COUNT(*) FROM images WHERE character_id = ? AND status = 'saved')
            WHERE id = ?
        """, (img["character_id"], img["character_id"]))

        conn.commit()
        conn.close()
        logger.info(f"Image {image_id} ({filename}) saved to favorites: {fav_file}")
        return True

    @staticmethod
    def remove_from_favorites(image_id: int, remove_file: bool = True) -> bool:
        """
        Removes image from favorites and physically deletes the favorite file from disk.
        """
        conn = get_connection()
        img = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        if not img:
            conn.close()
            return False

        # 1. Physically delete favorite file from disk
        if img["favorites_path"]:
            fav_path = Path(img["favorites_path"])
            if fav_path.exists() and remove_file:
                try:
                    fav_path.unlink()
                except Exception as e:
                    logger.warning(f"Error removing favorite file {fav_path}: {e}")

        # 2. Check if temp candidate file still exists
        temp_exists = img["temp_path"] and Path(img["temp_path"]).exists()
        new_status = "pending" if temp_exists else "deleted"

        conn.execute("""
            UPDATE images 
            SET status = ?, favorites_path = NULL 
            WHERE id = ?
        """, (new_status, image_id))

        conn.execute("""
            UPDATE characters 
            SET total_favorites = (SELECT COUNT(*) FROM images WHERE character_id = ? AND status = 'saved')
            WHERE id = ?
        """, (img["character_id"], img["character_id"]))

        conn.commit()
        conn.close()
        return True

    remove_favorite_image = remove_from_favorites

    @staticmethod
    def delete_single_image(image_id: int) -> bool:
        """
        Deletes the temporary candidate file and thumbnail.
        NEVER touches favorites folder if already favorited!
        """
        conn = get_connection()
        img = conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
        if not img:
            conn.close()
            return False

        # Delete temp file
        if img["temp_path"]:
            p = Path(img["temp_path"])
            if p.exists():
                try: p.unlink()
                except Exception: pass

        # Delete thumb file
        if img["thumbnail_path"]:
            tp = Path(img["thumbnail_path"])
            if tp.exists():
                try: tp.unlink()
                except Exception: pass

        # If it was favorited, keep DB record as 'saved' (with temp_path null)
        # If it was pending, delete or mark deleted
        if img["status"] == "saved":
            conn.execute("UPDATE images SET temp_path = NULL, thumbnail_path = NULL WHERE id = ?", (image_id,))
        else:
            conn.execute("DELETE FROM images WHERE id = ?", (image_id,))

        conn.execute("""
            UPDATE characters 
            SET total_candidates = (SELECT COUNT(*) FROM images WHERE character_id = ? AND status IN ('pending', 'saved'))
            WHERE id = ?
        """, (img["character_id"], img["character_id"]))

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def clean_character_temp(character_name: str) -> Dict[str, Any]:
        """
        CRITICAL FEATURE (十、筛选完成后的清理功能):
        Wipes ALL temporary files in /data/anime-gallery/temp/<character_name>/
        Wipes thumbnail cache in /data/anime-gallery/cache/<character_name>/
        STRICTLY PROTECTS /data/anime-gallery/favorites/<character_name>/ (NEVER TOUCHES IT!).
        """
        char_clean = character_name.strip()
        temp_dir = TEMP_DIR / char_clean
        cache_dir = CACHE_DIR / char_clean
        fav_dir = FAVORITES_DIR / char_clean

        cleaned_temp_files = 0
        cleaned_cache_files = 0

        # Clean temp directory
        if temp_dir.exists() and temp_dir.is_dir():
            for f in temp_dir.iterdir():
                if f.is_file():
                    try:
                        f.unlink()
                        cleaned_temp_files += 1
                    except Exception as e:
                        logger.error(f"Error removing temp file {f}: {e}")

        # Clean cache directory
        if cache_dir.exists() and cache_dir.is_dir():
            for f in cache_dir.iterdir():
                if f.is_file():
                    try:
                        f.unlink()
                        cleaned_cache_files += 1
                    except Exception as e:
                        logger.error(f"Error removing cache file {f}: {e}")

        # Update database: Unsaved candidate images marked as 'cleaned' or removed
        conn = get_connection()
        char_row = conn.execute("SELECT id FROM characters WHERE name = ?", (char_clean,)).fetchone()
        if char_row:
            char_id = char_row["id"]
            # Non-favorited images retain database metadata as 'cleaned' to ensure future searches NEVER re-download them!
            conn.execute("UPDATE images SET status = 'cleaned', temp_path = NULL, thumbnail_path = NULL WHERE character_id = ? AND status = 'pending'", (char_id,))
            # Favorited images retain status='saved', but clear temp_path
            conn.execute("UPDATE images SET temp_path = NULL WHERE character_id = ? AND status = 'saved'", (char_id,))
            
            # Recalculate active candidates total (only pending and saved)
            conn.execute("""
                UPDATE characters 
                SET total_candidates = (SELECT COUNT(*) FROM images WHERE character_id = ? AND status IN ('pending', 'saved'))
                WHERE id = ?
            """, (char_id, char_id))
            conn.commit()
        conn.close()

        logger.info(f"Cleaned {cleaned_temp_files} temp files and {cleaned_cache_files} thumbnails for '{char_clean}'. Favorites in {fav_dir} completely preserved.")
        return {
            "character_name": char_clean,
            "cleaned_temp_count": cleaned_temp_files,
            "cleaned_cache_count": cleaned_cache_files,
            "favorites_dir": str(fav_dir),
            "favorites_preserved": True
        }

    @staticmethod
    def get_storage_stats() -> Dict[str, Any]:
        """Calculates storage consumption for temp, favorites, and cache."""
        def dir_size_mb(path: Path) -> float:
            if not path.exists():
                return 0.0
            total = sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
            return round(total / (1024 * 1024), 2)

        return {
            "temp_mb": dir_size_mb(TEMP_DIR),
            "favorites_mb": dir_size_mb(FAVORITES_DIR),
            "cache_mb": dir_size_mb(CACHE_DIR),
            "total_mb": dir_size_mb(DATA_ROOT)
        }

    @staticmethod
    def cleanup_character_space(character_id: int, delete_favorites: bool = False) -> Dict[str, Any]:
        """
        Cleans up temporary candidate images and cache to free disk space.
        CRITICAL GUARANTEE: PRESERVES all favorited images in favorites/ folder and database by default!
        """
        import shutil
        conn = get_connection()
        char = conn.execute("SELECT * FROM characters WHERE id = ?", (character_id,)).fetchone()
        if not char:
            conn.close()
            return {"status": "error", "message": "Character not found"}

        char_name = char["name"]
        temp_dir = TEMP_DIR / char_name
        cache_dir = CACHE_DIR / char_name
        fav_dir = FAVORITES_DIR / char_name

        # 1. Delete temporary candidates folder (frees 99% disk space)
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Error removing temp dir {temp_dir}: {e}")

        # 2. If delete_favorites is explicitly True, remove favorites folder as well
        if delete_favorites and fav_dir.exists():
            try:
                shutil.rmtree(fav_dir)
            except Exception as e:
                logger.warning(f"Error removing fav dir {fav_dir}: {e}")

        # 3. Clean cache thumbnails for un-favorited candidates
        # (Preserve thumbnails of favorited images so favorites tab loads instantly)
        fav_rows = conn.execute("SELECT filename, thumbnail_path FROM images WHERE character_id = ? AND status = 'saved'", (character_id,)).fetchall()
        fav_filenames = {r["filename"] for r in fav_rows}

        if cache_dir.exists():
            if delete_favorites or not fav_filenames:
                try:
                    shutil.rmtree(cache_dir)
                except Exception as e:
                    logger.warning(f"Error removing cache dir {cache_dir}: {e}")
            else:
                for f in cache_dir.iterdir():
                    if f.is_file():
                        stem = f.stem.replace("thumb_", "")
                        if not any(stem in fn for fn in fav_filenames):
                            try:
                                f.unlink()
                            except Exception:
                                pass

        # 4. Database update
        if delete_favorites:
            conn.execute("DELETE FROM images WHERE character_id = ?", (character_id,))
            conn.execute("DELETE FROM tasks WHERE character_id = ?", (character_id,))
            conn.execute("DELETE FROM characters WHERE id = ?", (character_id,))
        else:
            # Delete non-favorited candidate images from images table
            conn.execute("DELETE FROM images WHERE character_id = ? AND status != 'saved'", (character_id,))
            conn.execute("DELETE FROM tasks WHERE character_id = ?", (character_id,))
            
            # Check remaining favorites count
            fav_count = len(fav_rows)
            if fav_count == 0:
                conn.execute("DELETE FROM characters WHERE id = ?", (character_id,))
            else:
                # Keep character in library with total_candidates = 0, retaining its favorites!
                conn.execute("""
                    UPDATE characters 
                    SET total_candidates = 0,
                        total_favorites = ?,
                        avatar_url = (SELECT thumbnail_path FROM images WHERE character_id = ? AND status = 'saved' LIMIT 1)
                    WHERE id = ?
                """, (fav_count, character_id, character_id))

        conn.commit()
        conn.close()

        msg = f"已释放角色【{char_name}】的临时候选空间！收藏夹中的 {len(fav_rows)} 张原画已完整保留。" if not delete_favorites else f"已彻底删除角色【{char_name}】全部数据。"
        return {
            "status": "success",
            "character_name": char_name,
            "favorites_preserved": not delete_favorites,
            "preserved_favorites_count": len(fav_rows) if not delete_favorites else 0,
            "message": msg
        }

    @staticmethod
    def export_favorites_zip(target_zip_path: Path) -> Path:
        """Packages all favorites across character folders into a clean ZIP archive."""
        import zipfile
        import os
        target_zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(FAVORITES_DIR):
                for file in files:
                    full_path = Path(root) / file
                    rel_path = full_path.relative_to(FAVORITES_DIR)
                    zipf.write(full_path, arcname=str(rel_path))
        return target_zip_path
