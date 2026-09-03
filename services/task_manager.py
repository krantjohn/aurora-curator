import uuid
import shutil
import asyncio
import logging
import httpx
from pathlib import Path
from typing import Dict, Optional, List, Any, Set, Tuple
from datetime import datetime
from config import DATA_ROOT
from database import get_connection
from models import TaskOut
from providers.manager import ProviderManager
from services.downloader import ImageDownloader
from services.image_processor import ImageProcessor
from services.storage_service import StorageService

logger = logging.getLogger("anime_gallery.services.task_manager")

class TaskManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.provider_manager = ProviderManager()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_controls: Dict[str, str] = {}  # 'running', 'paused', 'cancelled'

    def get_or_create_character(self, character_name: str) -> Tuple[int, int]:
        """Returns (character_id, current_page)."""
        clean_name = character_name.strip()
        slug = clean_name.replace(" ", "_").lower()
        conn = get_connection()
        row = conn.execute("SELECT id, current_page FROM characters WHERE name = ?", (clean_name,)).fetchone()
        if row:
            char_id = row["id"]
            current_page = row["current_page"] or 1
            conn.execute("UPDATE characters SET last_searched_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (char_id,))
        else:
            game = "other"
            aliases = None
            try:
                from services.character_catalog import CHARACTER_CATALOG
                import json
                for c in CHARACTER_CATALOG:
                    if c["name"] == clean_name or clean_name in c.get("aliases", []):
                        game = c["game"]
                        aliases = json.dumps(c.get("aliases", []), ensure_ascii=False)
                        break
            except Exception:
                pass
            cur = conn.execute("INSERT INTO characters (name, slug, game, aliases, current_page, last_searched_at) VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)", (clean_name, slug, game, aliases))
            char_id = cur.lastrowid
            current_page = 1
        conn.commit()
        conn.close()
        return char_id, current_page

    def update_task_db(self, task_id: str, **kwargs):
        conn = get_connection()
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        conn.execute(query, tuple(values))
        conn.commit()
        conn.close()

    def create_task(self, character_name: str, limit: int = 100, rating: str = "sfw") -> str:
        task_id = str(uuid.uuid4())[:8]
        clean_name = character_name.strip()
        rating_mode = "r18" if (rating or "").lower() in ["r18", "r-18", "nsfw"] else "sfw"
        char_id, current_page = self.get_or_create_character(clean_name)

        rating_desc = "R-18" if rating_mode == "r18" else "全年龄"
        conn = get_connection()
        max_batch_row = conn.execute("SELECT MAX(batch_number) FROM images WHERE character_id = ?", (char_id,)).fetchone()
        batch_num = (max_batch_row[0] or 0) + 1 if max_batch_row and max_batch_row[0] else 1

        conn.execute("""
            INSERT INTO tasks (id, character_name, character_id, rating, status, progress_current, progress_total, progress_message)
            VALUES (?, ?, ?, ?, 'queued', 0, ?, ?)
        """, (task_id, clean_name, char_id, rating_mode, limit, f"第 {batch_num} 批任务已进入队列 ({rating_desc})"))
        conn.commit()
        conn.close()

        self.task_controls[task_id] = "running"
        task = asyncio.create_task(self._run_task_pipeline(task_id, clean_name, char_id, limit, current_page, rating_mode, batch_num))
        self.active_tasks[task_id] = task

        return task_id

    async def _run_task_pipeline(self, task_id: str, character_name: str, character_id: int, limit: int, start_page: int, rating: str = "sfw", batch_num: int = 1):
        is_r18 = (rating == "r18")
        rating_label = "R-18" if is_r18 else "全年龄"
        logger.info(f"Starting pipeline for task {task_id} - Character: {character_name}, Batch #{batch_num}, Rating: {rating_label}, Limit: {limit}, Start Page: {start_page}")
        self.update_task_db(task_id, status="searching", progress_message=f"正在按【{rating_label}】热度检索第 {batch_num} 批原画 (起始第 {start_page} 页)...")

        # 1. 磁盘空间熔断安全检测
        try:
            usage = shutil.disk_usage(DATA_ROOT)
            pct_used = (usage.used / usage.total) * 100
            conn = get_connection()
            thresh_row = conn.execute("SELECT value FROM settings WHERE key = 'max_disk_usage_percent'").fetchone()
            conn.close()
            max_thresh = float(thresh_row["value"]) if thresh_row else 85.0

            if pct_used >= max_thresh:
                err_msg = f"服务器磁盘使用率已达 {pct_used:.1f}% (警报阈值 {max_thresh}%)，请先清理临时图片！"
                logger.warning(f"Task {task_id} aborted: {err_msg}")
                self.update_task_db(
                    task_id,
                    status="failed",
                    error_message=err_msg,
                    progress_message="磁盘空间不足，已自动暂停新任务"
                )
                return
        except Exception as e:
            logger.warning(f"Disk check error: {e}")

        try:
            # 2. 加载全量历史哈希与图片链接（用于永久历史去重）
            conn = get_connection()
            rows = conn.execute("SELECT phash, source_url, source_id, filename FROM images WHERE character_id = ?", (character_id,)).fetchall()
            max_row = conn.execute("SELECT MAX(CAST(SUBSTR(filename, 1, INSTR(filename, '.') - 1) AS INTEGER)) as max_num, COUNT(*) as cnt FROM images WHERE character_id = ?", (character_id,)).fetchone()
            max_num = max_row["max_num"] if max_row and max_row["max_num"] else (max_row["cnt"] if max_row else 0)
            start_index = (max_num or 0) + 1
            conn.close()

            existing_hashes: Set[str] = set()
            existing_source_urls: Set[str] = set()
            for r in rows:
                if r["phash"]: existing_hashes.add(r["phash"])
                if r["source_url"]: existing_source_urls.add(r["source_url"].split("?")[0])

            downloaded_count = 0
            page = start_page
            max_pages_to_scan = start_page + 12
            db_lock = asyncio.Lock()

            # 并发控制：10 个高并发 Worker 同时极速下载
            CONCURRENCY_LIMIT = 10
            sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
            limits = httpx.Limits(max_connections=35, max_keepalive_connections=25)

            async with httpx.AsyncClient(limits=limits, timeout=25.0) as client:
                while downloaded_count < limit and page <= max_pages_to_scan:
                    # 任务控制
                    ctrl = self.task_controls.get(task_id, "running")
                    if ctrl == "cancelled":
                        self.update_task_db(task_id, status="cancelled", progress_message="任务已由用户取消")
                        return

                    self.update_task_db(
                        task_id,
                        status="searching",
                        progress_message=f"正在检索第 {page} 页【{rating_label}】插画 (已收集 {downloaded_count}/{limit} 张)..."
                    )

                    # 多源并发检索
                    page_candidates = await self.provider_manager.search_all(
                        character_name,
                        limit=limit,
                        page=page,
                        sort_by_popularity=True,
                        rating=rating
                    )

                    if not page_candidates:
                        logger.info(f"No candidates found on page {page} for '{character_name}' ({rating_label}).")
                        break

                    # 过滤已下载过的 URL
                    filtered_candidates = []
                    for cand in page_candidates:
                        norm_url = cand.source_url.split("?")[0] if cand.source_url else ""
                        if not norm_url or norm_url not in existing_source_urls:
                            filtered_candidates.append(cand)

                    if not filtered_candidates:
                        page += 1
                        continue

                    # 定义单个 Worker 的极速下载与去重任务
                    async def fetch_and_save_worker(cand, current_idx):
                        nonlocal downloaded_count
                        if downloaded_count >= limit or self.task_controls.get(task_id) == "cancelled":
                            return

                        async with sem:
                            result = await ImageDownloader.download_and_process_candidate(
                                candidate=cand,
                                character_name=character_name,
                                index_num=current_idx,
                                client=client
                            )

                            if not result:
                                return

                            phash = result.get("phash")
                            norm_source_url = cand.source_url.split("?")[0] if cand.source_url else ""

                            # 线程安全入库与哈希碰撞检测
                            async with db_lock:
                                if downloaded_count >= limit:
                                    # Clean up extra downloaded file
                                    try: Path(result["temp_path"]).unlink(missing_ok=True)
                                    except Exception: pass
                                    try: Path(result["thumbnail_path"]).unlink(missing_ok=True)
                                    except Exception: pass
                                    return

                                # 比对感知哈希汉明距离
                                is_dup = False
                                if phash:
                                    if phash in existing_hashes:
                                        is_dup = True
                                    else:
                                        for eh in existing_hashes:
                                            if ImageProcessor.is_duplicate(phash, eh):
                                                is_dup = True
                                                break

                                if is_dup:
                                    try: Path(result["temp_path"]).unlink(missing_ok=True)
                                    except Exception: pass
                                    try: Path(result["thumbnail_path"]).unlink(missing_ok=True)
                                    except Exception: pass
                                    return

                                # 写入数据库 (包含 rating 属性)
                                img_rating = cand.rating or rating
                                conn = get_connection()
                                conn.execute("""
                                    INSERT INTO images (
                                        character_id, filename, temp_path, thumbnail_path, 
                                        original_source, source_url, source_id, author_name, 
                                        author_url, title, copyright_info, width, height, 
                                        file_size, phash, dhash, ahash, status, rating, batch_number, task_id, google_sync_status
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, 'not_synced')
                                """, (
                                    character_id, result["filename"], result["temp_path"], result["thumbnail_path"],
                                    result["original_source"], result["source_url"], result["source_id"], result["author_name"],
                                    result["author_url"], result["title"], result["copyright_info"], result["width"], result["height"],
                                    result["file_size"], result["phash"], result["dhash"], result["ahash"], img_rating, batch_num, task_id
                                ))
                                conn.commit()
                                conn.close()

                                if phash: existing_hashes.add(phash)
                                if norm_source_url: existing_source_urls.add(norm_source_url)
                                downloaded_count += 1

                                self.update_task_db(
                                    task_id,
                                    status="downloading",
                                    progress_current=downloaded_count,
                                    progress_total=limit,
                                    progress_message=f"⚡ 极速并发下载中 ({downloaded_count}/{limit}) · 第 {batch_num} 批【{rating_label}】原画入库"
                                )

                    # 批量分发并发 Worker
                    tasks = []
                    for c_idx, cand in enumerate(filtered_candidates):
                        idx_num = start_index + downloaded_count + len(tasks)
                        tasks.append(fetch_and_save_worker(cand, idx_num))

                    # 并发执行本页所有下载
                    await asyncio.gather(*tasks)
                    page += 1

            # 4. 更新角色页码
            conn = get_connection()
            conn.execute("""
                UPDATE characters 
                SET current_page = ?,
                    total_candidates = (SELECT COUNT(*) FROM images WHERE character_id = ? AND status IN ('pending', 'saved')),
                    avatar_url = (SELECT thumbnail_path FROM images WHERE character_id = ? AND thumbnail_path IS NOT NULL ORDER BY id ASC LIMIT 1)
                WHERE id = ?
            """, (page, character_id, character_id, character_id))
            conn.commit()
            conn.close()

            # 5. 完成汇报
            conn = get_connection()
            char_row = conn.execute("SELECT total_candidates FROM characters WHERE id = ?", (character_id,)).fetchone()
            total_in_lib = char_row["total_candidates"] if char_row else 0
            conn.close()

            if downloaded_count > 0:
                fin_msg = f"⚡ 第 {batch_num} 批收集完成！共获取 {downloaded_count} 张【{rating_label}】专属无损画作 (已自动去重)"
                fin_status = "completed"
                fin_total = downloaded_count
                fin_curr = downloaded_count
            elif total_in_lib > 0:
                fin_msg = f"✨ 该角色全网【{rating_label}】画作已全量收录（库中已有 {total_in_lib} 张，已自动跳过重复图片）"
                fin_status = "completed"
                fin_total = total_in_lib
                fin_curr = total_in_lib
            else:
                fin_msg = f"全网暂未检索到该角色的可用【{rating_label}】画作（请检查角色名称拼写）"
                fin_status = "empty"
                fin_total = 0
                fin_curr = 0

            self.update_task_db(
                task_id, 
                status=fin_status, 
                progress_current=fin_curr, 
                progress_total=fin_total,
                result_count=downloaded_count,
                progress_message=fin_msg
            )
            logger.info(f"Task {task_id} completed. Downloaded {downloaded_count} {rating_label} images for {character_name}. Total in lib: {total_in_lib}.")

        except Exception as e:
            logger.error(f"Task {task_id} encountered exception: {e}", exc_info=True)
            self.update_task_db(task_id, status="failed", error_message=str(e), progress_message=f"任务异常: {e}")
        finally:
            self.active_tasks.pop(task_id, None)

    def pause_task(self, task_id: str) -> bool:
        if task_id in self.task_controls:
            self.task_controls[task_id] = "paused"
            self.update_task_db(task_id, status="paused")
            return True
        return False

    def resume_task(self, task_id: str) -> bool:
        if task_id in self.task_controls:
            self.task_controls[task_id] = "running"
            self.update_task_db(task_id, status="downloading")
            return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        if task_id in self.task_controls:
            self.task_controls[task_id] = "cancelled"
            self.update_task_db(task_id, status="cancelled", progress_message="任务已取消")
            if task_id in self.active_tasks:
                self.active_tasks[task_id].cancel()
            return True
        return False
