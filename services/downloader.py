import re
import uuid
import httpx
import logging
import asyncio
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from models import ImageCandidate
from services.image_processor import ImageProcessor
from services.storage_service import StorageService

logger = logging.getLogger("anime_gallery.services.downloader")

_atomic_allocation_lock = asyncio.Lock()

class ImageDownloader:
    @staticmethod
    async def download_and_process_candidate(
        candidate: ImageCandidate,
        character_name: str,
        index_num: int,
        client: httpx.AsyncClient
    ) -> Optional[Dict[str, Any]]:
        """
        Asynchronously downloads a candidate image, generates thumbnail and hashes in a single pass,
        and saves candidate file to /data/anime-gallery/temp/<character_name>/<001.jpg> with 100% collision-free atomic indexing.
        """
        # Determine extension from url or fallback to .jpg
        ext = ".jpg"
        clean_url = candidate.image_url.split("?")[0].lower()
        if clean_url.endswith((".mp4", ".webm", ".zip", ".swf", ".gifv")):
            return None
        if clean_url.endswith(".png"): ext = ".png"
        elif clean_url.endswith(".webp"): ext = ".webp"
        elif clean_url.endswith(".jpeg"): ext = ".jpeg"

        temp_dir = StorageService.get_character_temp_dir(character_name)
        cache_dir = StorageService.get_character_cache_dir(character_name)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        if candidate.headers:
            headers.update(candidate.headers)

        if "pximg.net" in candidate.image_url:
            headers["Referer"] = "https://www.pixiv.net/"
        elif "donmai.us" in candidate.image_url:
            headers["Referer"] = "https://danbooru.donmai.us/"
            headers["User-Agent"] = "AnimeGallery/1.0 (contact: admin@localhost)"
        elif "xbooru.com" in candidate.image_url:
            headers["Referer"] = "https://xbooru.com/"
        elif "tbib.org" in candidate.image_url:
            headers["Referer"] = "https://tbib.org/"
        elif "yande.re" in candidate.image_url:
            headers["Referer"] = "https://yande.re/"

        try:
            download_url = candidate.image_url
            resp = await client.get(download_url, headers=headers, timeout=18.0)
            
            # Pixiv fallback: if 404 on png, try jpg; if 404 on original, try master1200
            if resp.status_code == 404 and "pximg.net" in download_url:
                if download_url.endswith(".png"):
                    resp = await client.get(download_url.replace(".png", ".jpg"), headers=headers, timeout=18.0)
                elif download_url.endswith(".jpg"):
                    resp = await client.get(download_url.replace(".jpg", ".png"), headers=headers, timeout=18.0)
                if resp.status_code != 200 and "_master1200" not in download_url:
                    master_fallback = re.sub(r"/img-original/img/(.+)_p0\.(png|jpg)", r"/img-master/img/\1_p0_master1200.jpg", download_url)
                    resp = await client.get(master_fallback, headers=headers, timeout=18.0)

            if resp.status_code != 200:
                logger.warning(f"Download failed with status {resp.status_code} for {candidate.image_url}")
                return None

            image_bytes = resp.content
            if len(image_bytes) < 1024:  # Corrupt / empty
                return None

            # Atomically allocate unique index and write master + thumbnail to avoid concurrent file collision
            async with _atomic_allocation_lock:
                cur_idx = index_num
                while (
                    (temp_dir / f"{cur_idx:03d}.png").exists() or 
                    (temp_dir / f"{cur_idx:03d}.jpg").exists() or 
                    (temp_dir / f"{cur_idx:03d}.jpeg").exists() or 
                    (temp_dir / f"{cur_idx:03d}.webp").exists() or
                    (cache_dir / f"thumb_{cur_idx:03d}.webp").exists()
                ):
                    cur_idx += 1

                filename = f"{cur_idx:03d}{ext}"
                temp_dest = temp_dir / filename
                thumb_dest = cache_dir / f"thumb_{cur_idx:03d}.webp"

                # Process image and compute hashes in threadpool
                width, height, file_size, phash, dhash, ahash = await asyncio.to_thread(
                    ImageProcessor.process_image_all, image_bytes, thumb_dest
                )

                # Save full resolution master temp image
                with open(temp_dest, "wb") as f:
                    f.write(image_bytes)

            return {
                "filename": filename,
                "temp_path": str(temp_dest),
                "thumbnail_path": str(thumb_dest),
                "original_source": candidate.source_name,
                "source_url": candidate.source_url,
                "source_id": candidate.source_id,
                "author_name": candidate.author_name,
                "author_url": candidate.author_url,
                "title": candidate.title or f"{character_name} - {filename}",
                "copyright_info": candidate.copyright_info,
                "width": width,
                "height": height,
                "file_size": file_size,
                "phash": phash,
                "dhash": dhash,
                "ahash": ahash
            }

        except Exception as e:
            logger.warning(f"Failed downloading {candidate.image_url}: {e}")
            return None
