import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "app_data" / "pro_english_ai.db"
DEFAULT_PROFILE_ID = "local-beta"


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with _connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL DEFAULT 'Learner',
                target_level TEXT NOT NULL DEFAULT 'B2',
                weekly_goal INTEGER NOT NULL DEFAULT 3,
                save_history INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                level TEXT NOT NULL,
                level_index INTEGER NOT NULL,
                reliability INTEGER NOT NULL,
                quality_score INTEGER NOT NULL,
                word_count INTEGER NOT NULL,
                result_json TEXT NOT NULL,
                FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                level TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                details_json TEXT,
                FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS task_completions (
                profile_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                completed_at TEXT NOT NULL,
                PRIMARY KEY (profile_id, task_id),
                FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_analyses_profile_created
            ON analyses(profile_id, created_at DESC);

            CREATE INDEX IF NOT EXISTS idx_assessments_profile_created
            ON assessments(profile_id, created_at DESC);
            """
        )
        assessment_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(assessments)").fetchall()
        }
        if "details_json" not in assessment_columns:
            connection.execute("ALTER TABLE assessments ADD COLUMN details_json TEXT")
        now = _utc_now()
        connection.execute(
            """
            INSERT OR IGNORE INTO profiles
                (id, display_name, target_level, weekly_goal, save_history, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (DEFAULT_PROFILE_ID, "Learner", "B2", 3, 0, now, now),
        )


def get_profile(profile_id=DEFAULT_PROFILE_ID):
    with _connection() as connection:
        row = connection.execute(
            "SELECT * FROM profiles WHERE id = ?",
            (profile_id,),
        ).fetchone()
    return dict(row) if row else None


def update_profile(
    display_name,
    target_level,
    weekly_goal,
    save_history,
    profile_id=DEFAULT_PROFILE_ID,
):
    display_name = display_name.strip()[:40] or "Learner"
    weekly_goal = max(1, min(int(weekly_goal), 14))
    with _connection() as connection:
        connection.execute(
            """
            UPDATE profiles
            SET display_name = ?, target_level = ?, weekly_goal = ?,
                save_history = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                display_name,
                target_level,
                weekly_goal,
                int(bool(save_history)),
                _utc_now(),
                profile_id,
            ),
        )
    return get_profile(profile_id)


def save_analysis(result, profile_id=DEFAULT_PROFILE_ID):
    with _connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO analyses
                (profile_id, created_at, level, level_index, reliability,
                 quality_score, word_count, result_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id,
                result["created_at"],
                result["level"],
                result["level_index"],
                result["reliability"],
                result["quality_score"],
                result["metrics"]["word_count"],
                json.dumps(result, ensure_ascii=False),
            ),
        )
    return cursor.lastrowid


def list_analyses(profile_id=DEFAULT_PROFILE_ID, limit=50):
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT result_json
            FROM analyses
            WHERE profile_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (profile_id, max(1, min(int(limit), 500))),
        ).fetchall()
    return [json.loads(row["result_json"]) for row in rows]


def save_assessment(
    level,
    score,
    total=10,
    details=None,
    profile_id=DEFAULT_PROFILE_ID,
):
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO assessments
                (profile_id, created_at, level, score, total, passed, details_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id,
                _utc_now(),
                level,
                int(score),
                int(total),
                int(score / total >= 0.7),
                json.dumps(details, ensure_ascii=False) if details else None,
            ),
        )


def get_latest_assessment(profile_id=DEFAULT_PROFILE_ID):
    with _connection() as connection:
        row = connection.execute(
            """
            SELECT level, score, total, passed, created_at, details_json
            FROM assessments
            WHERE profile_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (profile_id,),
        ).fetchone()
    if not row:
        return None
    result = dict(row)
    result["details"] = (
        json.loads(result.pop("details_json"))
        if result.get("details_json")
        else None
    )
    return result


def set_task_completed(task_id, completed=True, profile_id=DEFAULT_PROFILE_ID):
    with _connection() as connection:
        if completed:
            connection.execute(
                """
                INSERT OR REPLACE INTO task_completions
                    (profile_id, task_id, completed_at)
                VALUES (?, ?, ?)
                """,
                (profile_id, task_id, _utc_now()),
            )
        else:
            connection.execute(
                """
                DELETE FROM task_completions
                WHERE profile_id = ? AND task_id = ?
                """,
                (profile_id, task_id),
            )


def list_completed_tasks(profile_id=DEFAULT_PROFILE_ID):
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT task_id
            FROM task_completions
            WHERE profile_id = ?
            """,
            (profile_id,),
        ).fetchall()
    return {row["task_id"] for row in rows}


def get_dashboard_stats(profile_id=DEFAULT_PROFILE_ID):
    with _connection() as connection:
        analysis = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                AVG(reliability) AS average_reliability,
                AVG(quality_score) AS average_quality,
                MAX(created_at) AS last_analysis
            FROM analyses
            WHERE profile_id = ?
            """,
            (profile_id,),
        ).fetchone()
        assessment = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                AVG(CAST(score AS REAL) / total * 100) AS average_score,
                SUM(passed) AS passed
            FROM assessments
            WHERE profile_id = ?
            """,
            (profile_id,),
        ).fetchone()
        weekly = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM analyses
            WHERE profile_id = ?
              AND datetime(created_at) >= datetime('now', '-7 days')
            """,
            (profile_id,),
        ).fetchone()

    return {
        "analysis_total": int(analysis["total"] or 0),
        "average_reliability": round(float(analysis["average_reliability"] or 0)),
        "average_quality": round(float(analysis["average_quality"] or 0)),
        "last_analysis": analysis["last_analysis"],
        "assessment_total": int(assessment["total"] or 0),
        "average_assessment_score": round(float(assessment["average_score"] or 0)),
        "assessments_passed": int(assessment["passed"] or 0),
        "weekly_analyses": int(weekly["total"] or 0),
    }


def clear_profile_data(profile_id=DEFAULT_PROFILE_ID):
    with _connection() as connection:
        connection.execute("DELETE FROM analyses WHERE profile_id = ?", (profile_id,))
        connection.execute("DELETE FROM assessments WHERE profile_id = ?", (profile_id,))
        connection.execute("DELETE FROM task_completions WHERE profile_id = ?", (profile_id,))
