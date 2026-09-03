import re
import logging
import httpx
import urllib.parse
from typing import List, Optional
from models import ImageCandidate
from providers.base import BaseProvider

logger = logging.getLogger("anime_gallery.providers.twitter")

NSFW_KEYWORDS = {
    "nude", "naked", "nipples", "pussy", "penis", "sex", "erotic", "r-18", "r18", "r-18g", "nsfw",
    "bottomless", "uncensored", "anus", "masturbation", "cameltoe", "no_bra", "topless", "panties"
}

class TwitterArtProvider(BaseProvider):
    """
    Crawls high-popularity Twitter/X illustrations and fanart via aggregated high-score indexes.
    Prioritizes original artists and uncompressed master media.
    """
    def __init__(self):
        super().__init__(name="Twitter / X Fanart")

    @property
    def is_enabled(self) -> bool:
        return True

    async def search(self, character_tag: str, limit: int = 50, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        candidates: List[ImageCandidate] = []
        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                if is_r18:
                    # R-18 模式：自 Yande.re 检索带 Twitter 来源的 R-18 (rating:e) 专属插画
                    clean_tag = character_tag.strip().replace(" ", "_").lower()
                    tags = f"{clean_tag} twitter rating:e order:score" if sort_by_popularity else f"{clean_tag} twitter rating:e"
                    url = f"https://yande.re/post.json?tags={urllib.parse.quote(tags)}&limit={limit}&page={page}"
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                    resp = await client.get(url, headers=headers)
                    if resp.status_code == 200:
                        posts = resp.json()
                        if isinstance(posts, list):
                            for post in posts:
                                if post.get("rating") != "e":
                                    continue
                                img_url = post.get("file_url") or post.get("sample_url")
                                if not img_url:
                                    continue

                                source_url = post.get("source") or f"https://yande.re/post/show/{post.get('id')}"
                                artist_name = post.get("author", "Twitter Artist")
                                if "twitter.com/" in source_url or "x.com/" in source_url:
                                    match = re.search(r"(?:twitter\.com|x\.com)/([A-Za-z0-9_]+)", source_url)
                                    if match:
                                        artist_name = f"@{match.group(1)} (Twitter)"

                                candidates.append(ImageCandidate(
                                    image_url=img_url,
                                    source_name="Twitter / X",
                                    source_id=str(post.get("id")),
                                    source_url=source_url,
                                    title=f"{character_tag} on Twitter (R-18)",
                                    author_name=artist_name,
                                    author_url=source_url,
                                    tags=post.get("tags", "").split(),
                                    rating="r18",
                                    score=int(post.get("score", 0)),
                                    width=int(post.get("width", 0)) if post.get("width") else None,
                                    height=int(post.get("height", 0)) if post.get("height") else None
                                ))
                else:
                    # 全年龄模式：自 Safebooru 检索高分 Twitter 纯净插画
                    clean_tag = character_tag.strip().replace(" ", "_").lower()
                    tags = f"{clean_tag} twitter sort:score:desc" if sort_by_popularity else f"{clean_tag} twitter"
                    url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={urllib.parse.quote(tags)}&limit={limit}&pid={page - 1}"
                    resp = await client.get(url)
                    if resp.status_code == 200 and resp.text.strip().startswith("["):
                        posts = resp.json()
                        for post in posts:
                            if post.get("rating", "s") != "s":
                                continue

                            post_tags = post.get("tags", "").lower()
                            if any(k in post_tags for k in NSFW_KEYWORDS):
                                continue

                            img_url = post.get("file_url")
                            if not img_url:
                                sample_url = post.get("sample_url")
                                directory = post.get("directory")
                                image = post.get("image")
                                if directory and image:
                                    img_url = f"https://safebooru.org/images/{directory}/{image}"
                                elif sample_url:
                                    img_url = sample_url

                            if not img_url:
                                continue

                            source_url = post.get("source") or f"https://safebooru.org/index.php?page=post&s=view&id={post.get('id')}"
                            artist_name = "Twitter Artist"
                            if "twitter.com/" in source_url or "x.com/" in source_url:
                                match = re.search(r"(?:twitter\.com|x\.com)/([A-Za-z0-9_]+)", source_url)
                                if match:
                                    artist_name = f"@{match.group(1)} (Twitter)"

                            candidates.append(ImageCandidate(
                                image_url=img_url,
                                source_name="Twitter / X",
                                source_id=str(post.get("id")),
                                source_url=source_url,
                                title=f"{character_tag} on Twitter",
                                author_name=artist_name,
                                author_url=source_url,
                                tags=post_tags.split(),
                                rating="sfw",
                                score=int(post.get("score", 0)),
                                width=int(post.get("width", 0)) if post.get("width") else None,
                                height=int(post.get("height", 0)) if post.get("height") else None
                            ))

        except Exception as e:
            logger.error(f"TwitterArtProvider search error for {character_tag}: {e}")

        return candidates
