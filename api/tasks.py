from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from database import get_connection
from models import TaskCreate, TaskOut
from services.task_manager import TaskManager

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])
task_manager = TaskManager()

@router.post("", response_model=TaskOut)
async def create_task(req: TaskCreate):
    char_name = req.character_name.strip()
    if not char_name:
        raise HTTPException(status_code=400, detail="Character name cannot be empty")

    task_id = task_manager.create_task(character_name=char_name, limit=req.limit, rating=req.rating)

    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    return TaskOut(
        id=row["id"],
        character_name=row["character_name"],
        character_id=row["character_id"],
        rating=row["rating"] if "rating" in row.keys() and row["rating"] else "sfw",
        status=row["status"],
        progress_current=row["progress_current"],
        progress_total=row["progress_total"],
        progress_message=row["progress_message"],
        result_count=row["result_count"],
        error_message=row["error_message"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

@router.get("", response_model=List[TaskOut])
async def list_tasks(limit: int = 15):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()

    return [
        TaskOut(
            id=r["id"],
            character_name=r["character_name"],
            character_id=r["character_id"],
            rating=r["rating"] if "rating" in r.keys() and r["rating"] else "sfw",
            status=r["status"],
            progress_current=r["progress_current"],
            progress_total=r["progress_total"],
            progress_message=r["progress_message"],
            result_count=r["result_count"],
            error_message=r["error_message"],
            created_at=str(r["created_at"]),
            updated_at=str(r["updated_at"])
        )
        for r in rows
    ]

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskOut(
        id=row["id"],
        character_name=row["character_name"],
        character_id=row["character_id"],
        rating=row["rating"] if "rating" in row.keys() and row["rating"] else "sfw",
        status=row["status"],
        progress_current=row["progress_current"],
        progress_total=row["progress_total"],
        progress_message=row["progress_message"],
        result_count=row["result_count"],
        error_message=row["error_message"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"])
    )

@router.post("/{task_id}/pause")
async def pause_task(task_id: str):
    ok = task_manager.pause_task(task_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Task cannot be paused")
    return {"status": "success", "message": "Task paused"}

@router.post("/{task_id}/resume")
async def resume_task(task_id: str):
    ok = task_manager.resume_task(task_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Task cannot be resumed")
    return {"status": "success", "message": "Task resumed"}

@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    ok = task_manager.cancel_task(task_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    return {"status": "success", "message": "Task cancelled"}

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Deletes a specific task record from history."""
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Task record removed"}

@router.delete("")
async def clear_finished_tasks():
    """Cleans up all completed or cancelled tasks from history."""
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE status IN ('completed', 'cancelled', 'failed', 'empty')")
    conn.commit()
    conn.close()
    return {"status": "success", "message": "All finished tasks cleared"}
