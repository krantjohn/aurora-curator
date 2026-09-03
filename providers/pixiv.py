import re
import logging
import httpx
import urllib.parse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models import ImageCandidate
from providers.base import BaseProvider
from database import get_connection

logger = logging.getLogger("anime_gallery.providers.pixiv")

NSFW_KEYWORDS = {
    "nude", "naked", "nipples", "pussy", "penis", "sex", "erotic", "r-18", "r18", "r-18g", "nsfw",
    "bottomless", "uncensored", "anus", "masturbation", "cameltoe", "no_bra", "topless", "panties", "oppai"
}

PIXIV_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

class PixivProvider(BaseProvider):
    def __init__(self):
        super().__init__(name="Pixiv (Official & Direct Engine)")
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    @property
    def is_enabled(self) -> bool:
        # Always enabled! (Dual-Mode: App API with OAuth or Public High-Res AJAX Engine)
        return True

    def _get_refresh_token(self) -> Optional[str]:
        conn = get_connection()
        row = conn.execute("SELECT value FROM settings WHERE key = 'pixiv_refresh_token'").fetchone()
        conn.close()
        return row["value"].strip() if row and row["value"] else None

    async def _get_access_token(self) -> Optional[str]:
        if self._access_token and self._token_expires_at and datetime.now() < self._token_expires_at:
            return self._access_token

        refresh_token = self._get_refresh_token()
        if not refresh_token:
            return None

        auth_url = "https://oauth.secure.pixiv.net/auth/token"
        headers = {
            "User-Agent": "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": "MOBrBDSLxAIdFMoRRbBbacA0Gal",
            "client_secret": "lsACyCD94FhDUtGTXi3QzcFE2uU1hqt0KObZuUbt",
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(auth_url, data=data, headers=headers)
                if resp.status_code == 200:
                    token_data = resp.json()
                    self._access_token = token_data["response"]["access_token"]
                    expires_in = token_data["response"]["expires_in"]
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    logger.info("Pixiv App access token refreshed successfully.")
                    return self._access_token
        except Exception as e:
            logger.error(f"Pixiv authentication exception: {e}")
        return None

    async def search(self, character_name: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        candidates: List[ImageCandidate] = []
        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])

        # Mode A: If OAuth Token is configured, use official App API (which supports real authenticated R-18)
        token = await self._get_access_token()
        if token:
            try:
                candidates = await self._search_app_api(character_name, token, limit=limit, page=page, sort_by_popularity=sort_by_popularity, is_r18=is_r18)
                if candidates:
                    logger.info(f"Pixiv App API retrieved {len(candidates)} candidates for {character_name} (R18: {is_r18})")
                    return candidates
            except Exception as e:
                logger.warning(f"Pixiv App API search failed: {e}")

        # Mode B: Public High-Res Pixiv Engine (No OAuth Token required)
        # 注意：未登录的 Pixiv 公开搜索会屏蔽所有真实 R-18 原画，仅返回带有 R-18 字样但实际为全年龄的作品。
        # 因此在 R-18 模式下，未授权的公开 Pixiv 引擎直接熔断跳过，转由专业成人图站 (Danbooru/XBooru/TBIB) 抓取真正的 R-18 画作。
        if is_r18:
            logger.info("Pixiv Public Engine bypassed in R-18 mode (avoids unauthenticated SFW contamination).")
            return []

        try:
            candidates = await self._search_public_ajax(character_name, limit=limit, page=page, sort_by_popularity=sort_by_popularity, is_r18=False)
            logger.info(f"Pixiv Public Engine retrieved {len(candidates)} SFW candidates for {character_name}")
        except Exception as e:
            logger.error(f"Pixiv Public Engine search error: {e}")

        return candidates

    async def _search_app_api(self, character_name: str, token: str, limit: int, page: int, sort_by_popularity: bool, is_r18: bool = False) -> List[ImageCandidate]:
        candidates = []
        headers = {
            "User-Agent": "PixivAndroidApp/5.0.234 (Android 11; Pixel 5)",
            "Authorization": f"Bearer {token}",
            "Referer": "https://app-api.pixiv.net/",
        }

        if is_r18:
            query_word = f"{character_name} R-18"
            if sort_by_popularity and page == 1:
                query_word = f"{character_name} R-18 users入り"
        else:
            query_word = character_name
            if sort_by_popularity and page == 1:
                query_word = f"{character_name} users入り"

        offset = (page - 1) * limit
        sort_param = "popular_desc" if sort_by_popularity else "date_desc"

        url = f"https://app-api.pixiv.net/v1/search/illust?word={urllib.parse.quote(query_word)}&search_target=partial_match_for_tags&sort={sort_param}&offset={offset}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                illusts = data.get("illusts", [])

                for item in illusts:
                    x_restrict = item.get("x_restrict", 0)
                    sanity_level = item.get("sanity_level", 2)
                    tags = [t.get("name", "").lower() for t in item.get("tags", [])]
                    tags_str = " ".join(tags)
                    has_r18_tag = any(k in tags_str for k in ["r-18", "r18", "r-18g", "nsfw"])

                    if is_r18:
                        # 严格 R-18 判定：绝不包含全年龄！
                        if x_restrict == 0 and sanity_level < 5 and not has_r18_tag:
                            continue
                    else:
                        # 严格全年龄判定：绝不包含 R-18！
                        if x_restrict != 0:
                            continue
                        if sanity_level > 2:
                            continue
                        if any(k in tags_str for k in NSFW_KEYWORDS):
                            continue

                    illust_id = item.get("id")
                    meta_single = item.get("meta_single_page", {})
                    orig_url = meta_single.get("original_image_url")

                    if not orig_url:
                        meta_pages = item.get("meta_pages", [])
                        if meta_pages:
                            orig_url = meta_pages[0].get("image_urls", {}).get("original")

                    if not orig_url:
                        orig_url = item.get("image_urls", {}).get("large")

                    if not orig_url:
                        continue

                    user = item.get("user", {})
                    author_name = user.get("name")
                    author_id = user.get("id")
                    author_url = f"https://www.pixiv.net/users/{author_id}" if author_id else None
                    bookmarks = item.get("total_bookmarks", 0)

                    candidates.append(ImageCandidate(
                        image_url=orig_url,
                        source_name="Pixiv",
                        source_id=str(illust_id),
                        source_url=f"https://www.pixiv.net/artworks/{illust_id}",
                        title=item.get("title") or f"Pixiv Artwork #{illust_id}",
                        author_name=author_name,
                        author_url=author_url,
                        tags=tags,
                        rating="r18" if is_r18 else "sfw",
                        score=bookmarks,
                        width=item.get("width"),
                        height=item.get("height"),
                        headers={"Referer": "https://www.pixiv.net/"}
                    ))

        return candidates

    async def _search_public_ajax(self, character_name: str, limit: int, page: int, sort_by_popularity: bool, is_r18: bool = False) -> List[ImageCandidate]:
        candidates: List[ImageCandidate] = []
        headers = {
            "User-Agent": PIXIV_USER_AGENT,
            "Referer": "https://www.pixiv.net/",
            "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7",
            "Cookie": "p_ab_id=9; p_ab_id_2=7; p_ab_d_id=91029302;"
        }

        # Query Pixiv AJAX search
        if is_r18:
            query = f"{character_name.strip()} R-18"
            mode_param = "r18"
        else:
            query = character_name.strip()
            mode_param = "safe"

        url = f"https://www.pixiv.net/ajax/search/illustrations/{urllib.parse.quote(query)}?word={urllib.parse.quote(query)}&p={page}&mode={mode_param}"

        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning(f"Pixiv AJAX search returned {resp.status_code}")
                return []

            data = resp.json()
            illust_items = data.get("body", {}).get("illust", {}).get("data", [])

            for item in illust_items:
                if not isinstance(item, dict) or not item.get("id"):
                    continue

                illust_id = item.get("id")
                x_restrict = item.get("xRestrict", 0)
                sanity_level = item.get("sanityLevel", 2)
                tags = item.get("tags", [])
                tags_str = " ".join(str(t).lower() for t in tags) if isinstance(tags, list) else ""
                has_r18_tag = any(k in tags_str for k in ["r-18", "r18", "r-18g", "nsfw"])

                if is_r18:
                    # 严格 R-18 过滤：绝不混入全年龄！
                    if x_restrict == 0 and not has_r18_tag:
                        continue
                else:
                    # 严格全年龄过滤：绝不混入 R-18！
                    if x_restrict != 0:
                        continue
                    if sanity_level > 2:
                        continue
                    if any(k in tags_str for k in NSFW_KEYWORDS):
                        continue

                thumb_url = item.get("url")
                if not thumb_url:
                    continue

                orig_url = re.sub(r"/img-master/(.+)_square1200\.jpg", r"/img-master/\1_master1200.jpg", thumb_url)
                orig_url = re.sub(r"/c/[^/]+/", "/", orig_url)

                title = item.get("title") or f"Pixiv Artwork #{illust_id}"
                user_name = item.get("userName")
                user_id = item.get("userId")
                author_url = f"https://www.pixiv.net/users/{user_id}" if user_id else None
                bookmark_count = item.get("bookmarkCount") or item.get("likeCount") or 0

                candidates.append(ImageCandidate(
                    image_url=orig_url,
                    source_name="Pixiv",
                    source_id=str(illust_id),
                    source_url=f"https://www.pixiv.net/artworks/{illust_id}",
                    title=title,
                    author_name=user_name,
                    author_url=author_url,
                    tags=tags if isinstance(tags, list) else [],
                    rating="r18" if is_r18 else "sfw",
                    score=int(bookmark_count),
                    width=item.get("width"),
                    height=item.get("height"),
                    headers={"Referer": "https://www.pixiv.net/"}
                ))

        # Sort by popularity / bookmarks if requested
        if sort_by_popularity:
            candidates.sort(key=lambda c: c.score or 0, reverse=True)

        return candidates
