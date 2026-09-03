import re
import logging
import httpx
import urllib.parse
from typing import List
from models import ImageCandidate
from providers.base import BaseProvider
from database import get_connection

logger = logging.getLogger("anime_gallery.providers.safebooru")

NSFW_KEYWORDS = {
    "nude", "naked", "nipples", "pussy", "penis", "sex", "erotic", "r-18", "r18", "nsfw",
    "bottomless", "uncensored", "anus", "ass_grab", "breast_grab", "masturbation", "cameltoe",
    "groin", "undressing", "no_bra", "topless", "panties", "pantsu", "tribadism", "yuri_sex",
    "erect_nipples", "areola", "fellatio", "cunnilingus", "oral", "tentacles", "bondage"
}

class SafebooruProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="Safebooru")

    @property
    def is_enabled(self) -> bool:
        conn = get_connection()
        row = conn.execute("SELECT value FROM settings WHERE key = 'safebooru_enabled'").fetchone()
        conn.close()
        return not row or row["value"].lower() == "true"

    async def search(self, character_tag: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        if not self.is_enabled:
            return []

        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])
        # Safebooru 为纯全年龄站点，R-18 模式下必须严格返回空列表，绝不混入全年龄
        if is_r18:
            return []

        candidates = []
        query_tag = character_tag.strip().replace(" ", "_").lower()
        if sort_by_popularity:
            query_tag = f"{query_tag} sort:score:desc"

        pid = max(0, page - 1)
        url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={urllib.parse.quote(query_tag)}&limit={min(limit, 100)}&pid={pid}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200 and resp.text.strip().startswith("["):
                    posts = resp.json()
                    if isinstance(posts, list):
                        for post in posts:
                            # 1. 严格过滤敏感标签
                            tags = set(post.get("tags", "").lower().split())
                            if tags & NSFW_KEYWORDS:
                                continue

                            file_url = post.get("file_url")
                            if not file_url and post.get("directory") and post.get("image"):
                                file_url = f"https://safebooru.org/images/{post['directory']}/{post['image']}"
                            
                            if not file_url:
                                continue

                            preview_url = post.get("preview_url") or file_url
                            source_field = post.get("source", "")
                            
                            source_name = "Safebooru"
                            source_url = f"https://safebooru.org/index.php?page=post&s=view&id={post.get('id')}"

                            if "pixiv.net" in source_field:
                                source_name = "Pixiv"
                                source_url = source_field
                            elif "pximg.net" in source_field:
                                m = re.search(r"/(\d+)(?:_p\d+)?\.(?:jpg|png|webp)", source_field)
                                if m:
                                    source_name = "Pixiv"
                                    source_url = f"https://www.pixiv.net/artworks/{m.group(1)}"

                            candidates.append(ImageCandidate(
                                image_url=file_url,
                                source_url=source_url,
                                source_name=source_name,
                                source_id=str(post.get("id")),
                                author_name=post.get("owner", "Anime Artist"),
                                author_url=f"https://safebooru.org/index.php?page=account&s=profile&uname={post.get('owner', '')}",
                                title=f"{character_tag.title()} - #{post.get('id')}",
                                copyright_info="Pixiv / Safebooru Clean Archive (SFW)",
                                width=post.get("width"),
                                height=post.get("height"),
                                preview_url=preview_url,
                                rating="sfw",
                                score=post.get("score", 0)
                            ))
                            if len(candidates) >= limit:
                                break
        except Exception as e:
            logger.warning(f"Safebooru search error for {character_tag}: {e}")

        return candidates
