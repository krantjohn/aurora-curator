import re
import logging
import httpx
import urllib.parse
from typing import List
from models import ImageCandidate
from providers.base import BaseProvider
from database import get_connection

logger = logging.getLogger("anime_gallery.providers.zerochan")

class ZerochanProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="Zerochan")

    @property
    def is_enabled(self) -> bool:
        conn = get_connection()
        row = conn.execute("SELECT value FROM settings WHERE key = 'zerochan_enabled'").fetchone()
        conn.close()
        return not row or row["value"].lower() == "true"

    async def search(self, character_tag: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        if not self.is_enabled:
            return []

        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])
        # Zerochan 为全年龄社区，R-18 模式下严格返回空列表，绝不混入全年龄
        if is_r18:
            return []

        candidates = []
        formatted_name = character_tag.strip().replace("_", "+")
        sort_query = "s=fav&" if sort_by_popularity else ""
        url = f"https://www.zerochan.net/{urllib.parse.quote(formatted_name)}?json&{sort_query}p={page}&l={min(limit, 100)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items", [])
                    for item in items:
                        large_url = item.get("large") or item.get("thumbnail")
                        if not large_url:
                            continue
                        
                        candidates.append(ImageCandidate(
                            image_url=large_url,
                            source_url=f"https://www.zerochan.net/{item.get('id')}",
                            source_name="Zerochan",
                            source_id=str(item.get("id")),
                            author_name=item.get("author", "Zerochan Artist"),
                            author_url=f"https://www.zerochan.net/user/{item.get('author', '')}",
                            title=item.get("tag", character_tag.title()),
                            copyright_info="Zerochan Anime Community",
                            width=item.get("width"),
                            height=item.get("height"),
                            preview_url=item.get("thumbnail") or large_url,
                            rating="sfw"
                        ))
                        if len(candidates) >= limit:
                            break
        except Exception as e:
            logger.warning(f"Zerochan search error for {character_tag}: {e}")

        return candidates
