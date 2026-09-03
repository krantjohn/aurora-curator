import re
import logging
import httpx
import urllib.parse
from typing import List
from models import ImageCandidate
from providers.base import BaseProvider

logger = logging.getLogger("anime_gallery.providers.yande")

NSFW_KEYWORDS = {
    "nude", "naked", "nipples", "pussy", "penis", "sex", "erotic", "r-18", "r18", "nsfw",
    "bottomless", "uncensored", "anus", "ass_grab", "breast_grab", "masturbation", "cameltoe",
    "groin", "undressing", "no_bra", "topless", "panties", "pantsu", "tribadism", "yuri_sex",
    "erect_nipples", "areola", "fellatio", "cunnilingus", "oral", "tentacles", "bondage"
}

class YandeProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="Yande.re (High-Res)")

    @property
    def is_enabled(self) -> bool:
        return True

    async def search(self, character_tag: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        candidates = []
        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])
        clean_tag = character_tag.strip().replace(" ", "_").lower()
        
        # Rating filter: SFW (rating:s) vs R-18 (rating:e)
        rating_tag = "rating:e" if is_r18 else "rating:s"
        query_tags = f"{clean_tag} {rating_tag} order:score" if sort_by_popularity else f"{clean_tag} {rating_tag}"
        url = f"https://yande.re/post.json?tags={urllib.parse.quote(query_tags)}&limit={min(limit, 100)}&page={page}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    posts = resp.json()
                    if isinstance(posts, list):
                        for post in posts:
                            post_rating = post.get("rating")
                            tags = set(post.get("tags", "").lower().split())

                            if is_r18:
                                # 严格 R-18 过滤：绝不包含任何全年龄 Safe
                                if post_rating != "e":
                                    continue
                            else:
                                # 严格全年龄过滤：绝不包含任何 R-18
                                if post_rating != "s":
                                    continue
                                if tags & NSFW_KEYWORDS:
                                    continue

                            # 2. 优先获取 100% 无损原画 (file_url)
                            img_url = post.get("file_url") or post.get("sample_url")
                            if not img_url:
                                continue

                            author = post.get("author", "Anime Artist")
                            source_field = post.get("source", "")
                            
                            # 3. Detect Pixiv origin
                            source_name = "Yande.re"
                            source_url = f"https://yande.re/post/show/{post.get('id')}"
                            
                            if "pixiv.net" in source_field:
                                source_name = "Pixiv"
                                source_url = source_field
                            elif "pximg.net" in source_field:
                                m = re.search(r"/(\d+)(?:_p\d+)?\.(?:jpg|png|webp)", source_field)
                                if m:
                                    source_name = "Pixiv"
                                    source_url = f"https://www.pixiv.net/artworks/{m.group(1)}"

                            candidates.append(ImageCandidate(
                                image_url=img_url,
                                source_url=source_url,
                                source_name=source_name,
                                source_id=str(post.get("id")),
                                author_name=author,
                                author_url=f"https://yande.re/post?tags=user%3A{urllib.parse.quote(author)}",
                                title=f"{character_tag.title()} - #{post.get('id')}",
                                copyright_info="Pixiv / Yande High-Res Community",
                                width=post.get("width"),
                                height=post.get("height"),
                                preview_url=post.get("preview_url") or img_url,
                                rating="r18" if is_r18 else "sfw",
                                score=post.get("score", 0)
                            ))
                            if len(candidates) >= limit:
                                break
        except Exception as e:
            logger.warning(f"Yande.re search error for {character_tag}: {e}")

        return candidates
