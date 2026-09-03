import logging
import httpx
import urllib.parse
from typing import List
from models import ImageCandidate
from providers.base import BaseProvider

logger = logging.getLogger("anime_gallery.providers.xbooru")

class XBooruProvider(BaseProvider):
    """
    Dedicated R-18 / Adult Anime ImageBoard Provider.
    Strictly yields only R-18 / adult artworks and immediately bypasses in SFW mode.
    """
    def __init__(self):
        super().__init__(name="XBooru (Adult Archive)")

    @property
    def is_enabled(self) -> bool:
        return True

    async def search(self, character_tag: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])
        if not is_r18:
            # SFW 模式严格跳过成人图站
            return []

        candidates = []
        query_tag = character_tag.strip().replace(" ", "_").lower()
        url = f"https://xbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={urllib.parse.quote(query_tag)}&limit={min(limit, 100)}&pid={page - 1}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200 and resp.text.strip().startswith("["):
                    posts = resp.json()
                    if isinstance(posts, list):
                        for post in posts:
                            # 提取高清大图 URL
                            img_url = post.get("file_url")
                            directory = post.get("directory")
                            image = post.get("image")
                            if not img_url and directory and image:
                                img_url = f"https://img.xbooru.com/images/{directory}/{image}"

                            if not img_url:
                                continue

                            thumb_url = post.get("preview_url") or post.get("sample_url")
                            post_id = str(post.get("id"))
                            score_val = post.get("score")
                            try:
                                score_int = int(score_val) if score_val is not None else 0
                            except (ValueError, TypeError):
                                score_int = 0

                            candidates.append(ImageCandidate(
                                image_url=img_url,
                                source_url=f"https://xbooru.com/index.php?page=post&s=view&id={post_id}",
                                source_name="XBooru",
                                source_id=post_id,
                                author_name=post.get("owner", "XBooru Artist"),
                                author_url=None,
                                title=f"{character_tag.title()} - XBooru #{post_id}",
                                copyright_info="XBooru R-18 Community",
                                width=post.get("width"),
                                height=post.get("height"),
                                preview_url=thumb_url or img_url,
                                rating="r18",
                                score=score_int,
                                headers={"Referer": "https://xbooru.com/"}
                            ))
                            if len(candidates) >= limit:
                                break
        except Exception as e:
            logger.warning(f"XBooru search error for {character_tag}: {e}")

        return candidates
