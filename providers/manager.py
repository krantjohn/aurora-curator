import re
import asyncio
import logging
from typing import List, Tuple
from models import ImageCandidate
from providers.pixiv import PixivProvider
from providers.twitter import TwitterArtProvider
from providers.danbooru import DanbooruProvider
from providers.safebooru import SafebooruProvider
from providers.zerochan import ZerochanProvider
from providers.yande import YandeProvider
from providers.xbooru import XBooruProvider
from providers.tbib import TBIBProvider
from providers.aibooru import AIBooruProvider
from services.character_resolver import CharacterResolver

logger = logging.getLogger("anime_gallery.providers.manager")

class ProviderManager:
    def __init__(self):
        self.pixiv = PixivProvider()
        self.twitter = TwitterArtProvider()
        self.yande = YandeProvider()
        self.safebooru = SafebooruProvider()
        self.zerochan = ZerochanProvider()
        self.danbooru = DanbooruProvider()
        self.xbooru = XBooruProvider()
        self.tbib = TBIBProvider()
        self.aibooru = AIBooruProvider()

    async def search_all(self, character_name: str, limit: int = 100, page: int = 1, sort_by_popularity: bool = True, rating: str = "sfw") -> List[ImageCandidate]:
        is_r18 = (rating.lower() in ["r18", "r-18", "nsfw"])
        rating_mode = "r18" if is_r18 else "sfw"
        
        # 🧠 智能角色多级解析（静态大字典 + SQLite缓存 + Danbooru实时在线词典 + 拼音退避）
        booru_tags, pixiv_kw = await CharacterResolver.resolve(character_name)
        logger.info(f"Searching character '{character_name}' [Page {page}] [Mode: {rating_mode.upper()}] -> Pixiv: '{pixiv_kw}', Booru Tags: {booru_tags} (Popularity: {sort_by_popularity})")

        tasks = []

        if is_r18:
            # 🔞 R-18 专属海量高产出图源并发矩阵
            # 1. Danbooru (Explicit + Questionable)
            for tag in booru_tags[:3]:
                if self.danbooru.is_enabled:
                    tasks.append(self.danbooru.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="r18"))
            
            # 2. AIBooru (High-yield Explicit digital & AI artworks)
            for tag in booru_tags[:3]:
                if self.aibooru.is_enabled:
                    tasks.append(self.aibooru.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="r18"))

            # 3. TBIB (The Big ImageBoard Explicit & Questionable)
            for tag in booru_tags[:3]:
                if self.tbib.is_enabled:
                    tasks.append(self.tbib.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="r18"))

            # 4. XBooru (100% Dedicated Adult Archive)
            for tag in booru_tags[:3]:
                if self.xbooru.is_enabled:
                    tasks.append(self.xbooru.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="r18"))

            # 5. Yande.re (Explicit rating:e)
            for tag in booru_tags[:2]:
                if self.yande.is_enabled:
                    tasks.append(self.yande.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="r18"))

            # 6. Pixiv (仅在用户配置了 OAuth Token 时调用官方 App API，未授权公开 Pixiv 自动熔断跳过以防污染)
            if self.pixiv.is_enabled:
                tasks.append(self.pixiv.search(pixiv_kw, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="r18"))

        else:
            # 🛡️ 全年龄 (SFW) 专属纯净图源矩阵
            # 1. Pixiv Safe Engine
            if self.pixiv.is_enabled:
                tasks.append(self.pixiv.search(pixiv_kw, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="sfw"))
                if page == 1 and character_name != pixiv_kw:
                    tasks.append(self.pixiv.search(character_name, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="sfw"))

            # 2. Safebooru (100% SFW Safe)
            for tag in booru_tags[:3]:
                if self.safebooru.is_enabled:
                    tasks.append(self.safebooru.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="sfw"))

            # 3. Zerochan (General Anime SFW)
            for tag in booru_tags[:2]:
                if self.zerochan.is_enabled:
                    tasks.append(self.zerochan.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="sfw"))

            # 4. Danbooru (rating:g General Safe)
            for tag in booru_tags[:2]:
                if self.danbooru.is_enabled:
                    tasks.append(self.danbooru.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="sfw"))

            # 5. Twitter SFW Fanart Feed
            for tag in booru_tags[:2]:
                tasks.append(self.twitter.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="sfw"))

            # 6. Yande.re (rating:s Safe)
            for tag in booru_tags[:2]:
                if self.yande.is_enabled:
                    tasks.append(self.yande.search(tag, limit=limit, page=page, sort_by_popularity=sort_by_popularity, rating="sfw"))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_candidates: List[ImageCandidate] = []
        seen_urls = set()

        for res in results:
            if isinstance(res, list):
                for cand in res:
                    # 严格属性校验二次把关：确保零串味
                    if is_r18 and cand.rating != "r18":
                        continue
                    if not is_r18 and cand.rating == "r18":
                        continue

                    norm_url = cand.image_url.split("?")[0]
                    if norm_url not in seen_urls:
                        seen_urls.add(norm_url)
                        combined_candidates.append(cand)

        # 🌟 综合热度与画质智能排序
        def candidate_sort_key(c: ImageCandidate):
            src = c.source_name.lower()
            if "pixiv" in src or "pixiv" in (c.source_url or "").lower():
                src_rank = 0
            elif "twitter" in src or "twitter" in (c.source_url or "").lower() or "x.com" in (c.source_url or "").lower():
                src_rank = 1
            elif "danbooru" in src:
                src_rank = 2
            elif "tbib" in src or "xbooru" in src:
                src_rank = 3
            else:
                src_rank = 4
            
            score = c.score or 0
            return (src_rank, -score)

        combined_candidates.sort(key=candidate_sort_key)

        logger.info(f"Retrieved {len(combined_candidates)} total {rating_mode.upper()} candidates for '{character_name}' (Page {page}).")
        return combined_candidates
