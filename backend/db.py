import sqlite3
import json
from pathlib import Path
from backend.config import BASE_DIR

DB_PATH = BASE_DIR / "app_data.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        # 최근 작업 및 Resume 정보 저장 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            major_topic TEXT NOT NULL,
            sub_topic TEXT NOT NULL,
            current_index INTEGER DEFAULT 0,
            total_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        # 작업 상세 문제 저장 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question_num INTEGER,
            topic TEXT,
            sub_type TEXT,
            stem TEXT,
            choices TEXT,
            answer TEXT,
            solution TEXT,
            image_file TEXT,
            FOREIGN KEY (session_id) REFERENCES task_sessions (id)
        )
        """)
        conn.commit()

init_db()
