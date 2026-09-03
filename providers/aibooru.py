import logging
import httpx
import urllib.parse
from typing import List
from models import ImageCandidate
from providers.base import BaseProvider

logger = logging.getLogger("anime_gallery.providers.aibooru")

class AIBooruProvider(BaseProvider):
    """
    AIBooru Dedicated Anime Provider.
    Extracts high-yield Explicit (R-18) and Questionable digital anime artworks.
    """
    def __init__(self):
        super().__init__(name="AIBooru")

    @property
    def is_enabled(self) -> bool:
        return True

    async def search(self, character_tag: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])
        if not is_r18:
            return []

        candidates: List[ImageCandidate] = []
        clean_tag = character_tag.strip().replace(" ", "_").lower()
        rating_tag = "rating:e"
        order_tag = "order:score" if (sort_by_popularity and page == 1) else "order:id_desc"
        query_tags = f"{clean_tag} {rating_tag} {order_tag}"

        url = f"https://aibooru.online/posts.json?tags={urllib.parse.quote(query_tags)}&limit={min(limit, 100)}&page={page}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    posts = resp.json()
                    if isinstance(posts, list):
                        for post in posts:
                            # Prefer uncompressed original file_url, then large_file_url
                            img_url = post.get("file_url") or post.get("large_file_url")
                            if not img_url:
                                continue

                            # Skip video formats
                            clean_img_url = img_url.split("?")[0].lower()
                            if clean_img_url.endswith((".mp4", ".webm", ".zip", ".swf")):
                                continue

                            thumb_url = post.get("preview_file_url") or post.get("large_file_url") or img_url
                            post_id = str(post.get("id"))
                            score_val = post.get("score")
                            try:
                                score_int = int(score_val) if score_val is not None else 0
                            except (ValueError, TypeError):
                                score_int = 0

                            candidates.append(ImageCandidate(
                                image_url=img_url,
                                source_url=f"https://aibooru.online/posts/{post_id}",
                                source_name="AIBooru",
                                source_id=post_id,
                                author_name=post.get("tag_string_artist", "AIBooru Artist"),
                                author_url=None,
                                title=f"{character_tag.title()} - AIBooru #{post_id}",
                                copyright_info="AIBooru R-18 Archive",
                                width=post.get("image_width"),
                                height=post.get("image_height"),
                                preview_url=thumb_url,
                                rating="r18",
                                score=score_int,
                                headers={"Referer": "https://aibooru.online/"}
                            ))
                            if len(candidates) >= limit:
                                break
        except Exception as e:
            logger.warning(f"AIBooru search error for {character_tag}: {e}")

        return candidates
