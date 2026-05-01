import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from automaton_os.core.config import load_settings
from automaton_os.memory.obsidian import (
    update_mission_index,
    update_mission_queue_index,
    update_mission_detail_notes,
)


def get_db_path() -> Path:
    settings = load_settings()
    memory_config = settings.get("memory", {})

    db_path = memory_config.get("sqlite_path", "memory/automaton_os.db")
    path = Path(db_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    return path


def init_mission_log() -> None:
    db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mission_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            mission TEXT NOT NULL,
            status TEXT NOT NULL,
            administrator_decision TEXT NOT NULL,
            crew_name TEXT,
            saved_path TEXT,
            result_summary TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mission_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            mission TEXT NOT NULL,
            status TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 3,
            result_log_id INTEGER
        )
    """)

    conn.commit()
    conn.close()


def save_mission_log(
    mission: str,
    status: str,
    administrator_decision: dict,
    crew_name: str | None = None,
    saved_path: str | None = None,
    result_summary: str | None = None,
) -> dict:
    init_mission_log()

    created_at = datetime.now().isoformat(timespec="seconds")
    db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO mission_logs (
            created_at,
            mission,
            status,
            administrator_decision,
            crew_name,
            saved_path,
            result_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            created_at,
            mission,
            status,
            json.dumps(administrator_decision, ensure_ascii=False),
            crew_name,
            saved_path,
            result_summary,
        ),
    )

    log_id = cursor.lastrowid

    conn.commit()
    conn.close()

    recent_logs = list_mission_logs(limit=20)
    index_result = update_mission_index(recent_logs["logs"])

    return {
        "status": "saved",
        "id": log_id,
        "created_at": created_at,
        "db_path": str(db_path),
        "obsidian_index": index_result,
    }


def list_mission_logs(limit: int = 10) -> dict:
    init_mission_log()

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            created_at,
            mission,
            status,
            administrator_decision,
            crew_name,
            saved_path,
            result_summary
        FROM mission_logs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    logs: list[dict[str, Any]] = []

    for row in rows:
        (
            log_id,
            created_at,
            mission,
            status,
            administrator_decision,
            crew_name,
            saved_path,
            result_summary,
        ) = row

        try:
            parsed_decision = json.loads(administrator_decision)
        except json.JSONDecodeError:
            parsed_decision = administrator_decision

        logs.append({
            "id": log_id,
            "created_at": created_at,
            "mission": mission,
            "status": status,
            "administrator_decision": parsed_decision,
            "crew_name": crew_name,
            "saved_path": saved_path,
            "result_summary": result_summary,
        })

    return {
        "status": "ok",
        "logs": logs,
        "count": len(logs),
        "db_path": str(db_path),
    }


def add_queued_mission(mission: str, priority: int = 3) -> dict:
    init_mission_log()

    now = datetime.now().isoformat(timespec="seconds")
    db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    normalized_mission = mission.strip().lower()

    cursor.execute(
        """
        SELECT id, mission, status, priority
        FROM mission_queue
        WHERE lower(mission) = ?
        AND status IN ('pending', 'running')
        LIMIT 1
        """,
        (normalized_mission,),
    )

    existing = cursor.fetchone()

    if existing:
        conn.close()
        mission_id, existing_mission, existing_status, existing_priority = existing

        index_result = refresh_mission_queue_index()

        return {
            "status": "duplicate",
            "message": "A similar pending or running mission already exists.",
            "mission": {
                "id": mission_id,
                "mission": existing_mission,
                "status": existing_status,
                "priority": existing_priority,
            },
            "obsidian_queue_index": index_result,
        }

    cursor.execute(
        """
        INSERT INTO mission_queue (
            created_at,
            updated_at,
            mission,
            status,
            priority,
            result_log_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            now,
            now,
            mission,
            "pending",
            priority,
            None,
        ),
    )

    mission_id = cursor.lastrowid

    conn.commit()
    conn.close()

    index_result = refresh_mission_queue_index()

    return {
        "status": "created",
        "mission": {
            "id": mission_id,
            "mission": mission,
            "status": "pending",
            "priority": priority,
        },
        "obsidian_queue_index": index_result,
    }


def list_queued_missions(status: str | None = None, limit: int = 20) -> dict:
    init_mission_log()

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if status:
        cursor.execute(
            """
            SELECT id, created_at, updated_at, mission, status, priority, result_log_id
            FROM mission_queue
            WHERE status = ?
            ORDER BY priority ASC, id ASC
            LIMIT ?
            """,
            (status, limit),
        )
    else:
        cursor.execute(
            """
            SELECT id, created_at, updated_at, mission, status, priority, result_log_id
            FROM mission_queue
            ORDER BY priority ASC, id ASC
            LIMIT ?
            """,
            (limit,),
        )

    rows = cursor.fetchall()
    conn.close()

    missions = []

    for row in rows:
        (
            mission_id,
            created_at,
            updated_at,
            mission,
            mission_status,
            priority,
            result_log_id,
        ) = row

        missions.append({
            "id": mission_id,
            "created_at": created_at,
            "updated_at": updated_at,
            "mission": mission,
            "status": mission_status,
            "priority": priority,
            "result_log_id": result_log_id,
        })

    return {
        "status": "ok",
        "missions": missions,
        "count": len(missions),
        "db_path": str(db_path),
    }


def get_next_pending_mission() -> dict:
    queued = list_queued_missions(status="pending", limit=1)

    if queued["count"] == 0:
        return {
            "status": "empty",
            "message": "No pending missions in queue.",
            "mission": None,
        }

    return {
        "status": "ok",
        "mission": queued["missions"][0],
    }


def update_queued_mission_status(
    mission_id: int,
    status: str,
    result_log_id: int | None = None,
) -> dict:
    init_mission_log()

    allowed_statuses = {"pending", "running", "completed", "failed"}

    if status not in allowed_statuses:
        return {
            "status": "error",
            "error": f"Invalid queue mission status: {status}",
        }

    now = datetime.now().isoformat(timespec="seconds")
    db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE mission_queue
        SET status = ?, updated_at = ?, result_log_id = COALESCE(?, result_log_id)
        WHERE id = ?
        """,
        (
            status,
            now,
            result_log_id,
            mission_id,
        ),
    )

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    if changed == 0:
        return {
            "status": "error",
            "error": f"Queued mission not found: {mission_id}",
        }

    index_result = refresh_mission_queue_index()

    return {
        "status": "updated",
        "mission_id": mission_id,
        "new_status": status,
        "result_log_id": result_log_id,
        "obsidian_queue_index": index_result,
    }


def refresh_mission_queue_index(limit: int = 50) -> dict:
    queued = list_queued_missions(status=None, limit=limit)

    mission_logs_by_id = {}

    for item in queued["missions"]:
        result_log_id = item.get("result_log_id")

        if result_log_id:
            try:
                log = get_mission_log_by_id(int(result_log_id))
                if log:
                    mission_logs_by_id[int(result_log_id)] = log
            except ValueError:
                pass

    queue_index = update_mission_queue_index(queued["missions"])
    detail_notes = update_mission_detail_notes(
        queued["missions"],
        mission_logs_by_id=mission_logs_by_id,
    )

    return {
        "status": "saved",
        "queue_index": queue_index,
        "mission_detail_notes": detail_notes,
    }


def get_mission_log_by_id(log_id: int) -> dict | None:
    init_mission_log()

    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            created_at,
            mission,
            status,
            administrator_decision,
            crew_name,
            saved_path,
            result_summary
        FROM mission_logs
        WHERE id = ?
        LIMIT 1
        """,
        (log_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    (
        mission_log_id,
        created_at,
        mission,
        status,
        administrator_decision,
        crew_name,
        saved_path,
        result_summary,
    ) = row

    try:
        parsed_decision = json.loads(administrator_decision)
    except json.JSONDecodeError:
        parsed_decision = administrator_decision

    return {
        "id": mission_log_id,
        "created_at": created_at,
        "mission": mission,
        "status": status,
        "administrator_decision": parsed_decision,
        "crew_name": crew_name,
        "saved_path": saved_path,
        "result_summary": result_summary,
    }