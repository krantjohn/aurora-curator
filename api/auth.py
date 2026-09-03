import secrets
import logging
from typing import Optional, List, Tuple
from fastapi import APIRouter, Request, Response, HTTPException
from database import get_connection

logger = logging.getLogger("anime_gallery.api.auth")

router = APIRouter(prefix="/api/auth", tags=["Auth"])

def get_master_magic_key() -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = 'master_magic_key'").fetchone()
    if row and row["value"]:
        key = row["value"]
        conn.close()
        return key
    
    new_key = secrets.token_hex(20)  # 40-char high-entropy random key
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value, description) VALUES (?, ?, ?)",
        ("master_magic_key", new_key, "一键隐形专属配对通行密钥")
    )
    conn.commit()
    conn.close()
    return new_key

def get_current_token(request: Request) -> Optional[str]:
    # 1. Bearer token in Header
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "").strip()
    
    # 2. Cookie auth_token
    token_cookie = request.cookies.get("auth_token")
    if token_cookie:
        return token_cookie.strip()

    # 3. Query param token
    query_token = request.query_params.get("token") or request.query_params.get("key") or request.query_params.get("auth_key")
    if query_token:
        return query_token.strip()

    return None

def verify_token_in_db(token: str) -> Optional[dict]:
    if not token:
        return None
    try:
        conn = get_connection()
        row = conn.execute("SELECT * FROM authorized_devices WHERE token = ?", (token,)).fetchone()
        if row:
            # Update last active timestamp
            conn.execute("UPDATE authorized_devices SET last_active = CURRENT_TIMESTAMP WHERE id = ?", (row["id"],))
            conn.commit()
            res = dict(row)
            conn.close()
            return res
        conn.close()
    except Exception as e:
        logger.error(f"Token verification error: {e}")
    return None

def is_private_auth_enabled() -> bool:
    try:
        conn = get_connection()
        row = conn.execute("SELECT value FROM settings WHERE key = 'private_auth_enabled'").fetchone()
        conn.close()
        if row and row["value"]:
            return row["value"].strip().lower() in ("true", "1", "yes", "on")
    except Exception as e:
        logger.error(f"Error checking private_auth_enabled: {e}")
    return False

def verify_request_access(request: Request) -> Tuple[bool, Optional[str]]:
    """
    Validates request. Returns (is_authorized, new_device_token_to_set_cookie).
    """
    # 0. If private access protection is disabled, allow public access to all visitors
    if not is_private_auth_enabled():
        return (True, None)

    master_key = get_master_magic_key()

    # 1. Magic Passkey activation in query string (?key=... or ?auth_key=...)
    magic_param = request.query_params.get("key") or request.query_params.get("auth_key")
    if magic_param and magic_param.strip() == master_key.strip():
        # Generate 10-year persistent device token
        token = secrets.token_hex(32)
        user_agent = request.headers.get("user-agent", "Unknown")
        ip_addr = request.client.host if request.client else "Unknown"

        ua_lower = user_agent.lower()
        if "iphone" in ua_lower or "ipad" in ua_lower:
            device_name = "我的 Apple 手机/平板"
        elif "android" in ua_lower:
            device_name = "我的 Android 手机"
        elif "macintosh" in ua_lower or "mac os" in ua_lower:
            device_name = "我的 Mac 电脑"
        elif "windows" in ua_lower:
            device_name = "我的 Windows 电脑"
        else:
            device_name = "我的个人专属设备"

        try:
            conn = get_connection()
            conn.execute("""
                INSERT INTO authorized_devices (token, device_name, ip_address, user_agent)
                VALUES (?, ?, ?, ?)
            """, (token, device_name, ip_addr, user_agent))
            conn.commit()
            conn.close()
            logger.info(f"Magic Link authorized new device: '{device_name}' from IP: {ip_addr}")
        except Exception as e:
            logger.error(f"Failed to record authorized device: {e}")

        return (True, token)

    # 2. Token in Bearer header, Cookie, or Query parameter
    token = get_current_token(request)
    if token:
        # Check if token is the master magic key itself
        if token.strip() == master_key.strip():
            return (True, None)
        # Or check if token is in authorized_devices table
        dev = verify_token_in_db(token)
        if dev:
            return (True, None)

    return (False, None)

@router.get("/status")
async def get_auth_status(request: Request):
    auth_enabled = is_private_auth_enabled()
    token = get_current_token(request)
    device_info = verify_token_in_db(token) if token else None

    return {
        "auth_enabled": auth_enabled,
        "is_authenticated": (device_info is not None) or (not auth_enabled),
        "device_name": device_info.get("device_name") if device_info else ("全网公开访问模式" if not auth_enabled else None),
        "device_id": device_info.get("id") if device_info else None
    }

@router.get("/magic_info")
async def get_magic_info(request: Request):
    token = get_current_token(request)
    is_auth, _ = verify_request_access(request)
    if not is_auth:
        raise HTTPException(status_code=404, detail="Not Found")

    key = get_master_magic_key()
    host = request.headers.get("host") or (request.client.host if request.client else "localhost:8088")
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme
    path_prefix = "/gallery" if "/gallery" in request.url.path else ""
    magic_url = f"{scheme}://{host}{path_prefix}/?key={key}"

    return {
        "magic_key": key,
        "magic_url": magic_url
    }

@router.post("/reset_magic_key")
async def reset_magic_key(request: Request):
    is_auth, _ = verify_request_access(request)
    if not is_auth:
        raise HTTPException(status_code=404, detail="Not Found")

    new_key = secrets.token_hex(20)
    conn = get_connection()
    conn.execute(
        "UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = 'master_magic_key'",
        (new_key,)
    )
    conn.commit()
    conn.close()

    host = request.headers.get("host") or (request.client.host if request.client else "localhost:8088")
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme
    path_prefix = "/gallery" if "/gallery" in request.url.path else ""
    magic_url = f"{scheme}://{host}{path_prefix}/?key={new_key}"

    logger.info("Master magic key has been reset.")
    return {
        "status": "success",
        "message": "已生成新的专属授权链接",
        "magic_key": new_key,
        "magic_url": magic_url
    }

@router.get("/devices")
async def list_authorized_devices(request: Request):
    is_auth, _ = verify_request_access(request)
    if not is_auth:
        raise HTTPException(status_code=404, detail="Not Found")

    conn = get_connection()
    rows = conn.execute("SELECT id, device_name, ip_address, user_agent, last_active, created_at FROM authorized_devices ORDER BY last_active DESC").fetchall()
    conn.close()

    return [dict(r) for r in rows]

@router.delete("/devices/{device_id}")
async def revoke_device(device_id: int, request: Request):
    is_auth, _ = verify_request_access(request)
    if not is_auth:
        raise HTTPException(status_code=404, detail="Not Found")

    conn = get_connection()
    conn.execute("DELETE FROM authorized_devices WHERE id = ?", (device_id,))
    conn.commit()
    conn.close()

    return {"status": "success", "message": f"设备 #{device_id} 授权已吊销"}
