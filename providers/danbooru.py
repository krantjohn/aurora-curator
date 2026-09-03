import logging
import httpx
import urllib.parse
from typing import List
from models import ImageCandidate
from providers.base import BaseProvider
from database import get_connection

logger = logging.getLogger("anime_gallery.providers.danbooru")

class DanbooruProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="Danbooru")

    @property
    def is_enabled(self) -> bool:
        conn = get_connection()
        row = conn.execute("SELECT value FROM settings WHERE key = 'danbooru_enabled'").fetchone()
        conn.close()
        return row and row["value"].lower() == "true"

    async def search(self, character_tag: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        if not self.is_enabled:
            return []

        candidates = []
        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])
        query_tag = character_tag.strip().replace(" ", "_").lower()
        sort_filter = "+order:score" if (sort_by_popularity and page == 1) else "+order:id_desc"

        headers = {
            "User-Agent": "AnimeGalleryManager/1.0 (Open-source Personal Archive Client)"
        }

        # Determine rating filters to query
        rating_filters = ["rating:e", "rating:q"] if is_r18 else ["rating:g"]

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
                for r_filter in rating_filters:
                    url = f"https://danbooru.donmai.us/posts.json?tags={urllib.parse.quote(query_tag)}+{r_filter}{sort_filter}&limit={min(limit, 100)}&page={page}"
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        posts = resp.json()
                        if isinstance(posts, list):
                            for post in posts:
                                post_rating = post.get("rating")
                                if is_r18 and post_rating not in ["e", "q"]:
                                    continue
                                if not is_r18 and post_rating != "g":
                                    continue

                                file_url = post.get("file_url") or post.get("large_file_url")
                                if not file_url:
                                    continue

                                clean_file_url = file_url.split("?")[0].lower()
                                if clean_file_url.endswith((".mp4", ".webm", ".zip", ".swf")):
                                    continue
                                
                                artist = post.get("tag_string_artist", "Unknown Artist").replace("_", " ")
                                copyright_tag = post.get("tag_string_copyright", "").replace("_", " ")
                                post_id = str(post.get("id"))
                                
                                candidates.append(ImageCandidate(
                                    image_url=file_url,
                                    source_url=f"https://danbooru.donmai.us/posts/{post_id}",
                                    source_name="Danbooru",
                                    source_id=post_id,
                                    author_name=artist if artist else "Danbooru Creator",
                                    author_url=f"https://danbooru.donmai.us/posts?tags={urllib.parse.quote(post.get('tag_string_artist', ''))}" if post.get('tag_string_artist') else None,
                                    title=f"{character_tag.title()} - Post #{post_id}",
                                    copyright_info=copyright_tag or "Anime Character Art",
                                    width=post.get("image_width"),
                                    height=post.get("image_height"),
                                    preview_url=post.get("preview_file_url") or post.get("large_file_url"),
                                    rating="r18" if is_r18 else "sfw",
                                    score=post.get("score", 0),
                                    headers={"Referer": "https://danbooru.donmai.us/"}
                                ))
                                if len(candidates) >= limit:
                                    break
                    if len(candidates) >= limit:
                        break
        except Exception as e:
            logger.warning(f"Danbooru search error: {e}")

        return candidates
