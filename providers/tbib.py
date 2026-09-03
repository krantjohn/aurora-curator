import logging
import httpx
import urllib.parse
from typing import List
from models import ImageCandidate
from providers.base import BaseProvider

logger = logging.getLogger("anime_gallery.providers.tbib")

class TBIBProvider(BaseProvider):
    """
    The Big ImageBoard (TBIB) R-18 Explicit Artwork Provider.
    Extracts high-resolution explicit and questionable images and immediately bypasses in SFW mode.
    """
    def __init__(self):
        super().__init__(name="TBIB")

    @property
    def is_enabled(self) -> bool:
        return True

    async def search(self, character_tag: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])
        if not is_r18:
            return []

        candidates = []
        clean_tag = character_tag.strip().replace(" ", "_").lower()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

        rating_tags = ["rating:explicit", "rating:questionable"]

        try:
            async with httpx.AsyncClient(timeout=8.0, headers=headers) as client:
                for r_tag in rating_tags:
                    tags = f"{clean_tag} {r_tag}"
                    url = f"https://tbib.org/index.php?page=dapi&s=post&q=index&json=1&tags={urllib.parse.quote(tags)}&limit={min(limit, 100)}&pid={page - 1}"
                    resp = await client.get(url)
                    if resp.status_code == 200 and resp.text.strip().startswith("["):
                        posts = resp.json()
                        if isinstance(posts, list):
                            for post in posts:
                                img_url = post.get("file_url")
                                directory = post.get("directory")
                                image = post.get("image")
                                if not img_url and directory and image:
                                    img_url = f"https://tbib.org/images/{directory}/{image}"

                                if not img_url:
                                    continue

                                clean_img_url = img_url.split("?")[0].lower()
                                if clean_img_url.endswith((".mp4", ".webm", ".zip", ".swf")):
                                    continue

                                thumb_url = f"https://tbib.org/thumbnails/{directory}/thumbnail_{image}" if directory and image else img_url
                                post_id = str(post.get("id"))
                                score_val = post.get("score")
                                try:
                                    score_int = int(score_val) if score_val is not None else 0
                                except (ValueError, TypeError):
                                    score_int = 0

                                candidates.append(ImageCandidate(
                                    image_url=img_url,
                                    source_url=f"https://tbib.org/index.php?page=post&s=view&id={post_id}",
                                    source_name="TBIB",
                                    source_id=post_id,
                                    author_name=post.get("owner", "TBIB Artist"),
                                    author_url=None,
                                    title=f"{character_tag.title()} - TBIB #{post_id}",
                                    copyright_info="TBIB Explicit Community",
                                    width=post.get("width"),
                                    height=post.get("height"),
                                    preview_url=thumb_url,
                                    rating="r18",
                                    score=score_int,
                                    headers={"Referer": "https://tbib.org/"}
                                ))
                                if len(candidates) >= limit:
                                    break
                    if len(candidates) >= limit:
                        break
        except Exception as e:
            logger.warning(f"TBIB search error for {character_tag}: {e}")

        return candidates
