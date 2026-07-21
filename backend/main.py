from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio

try:
    from backend.config import set_api_keys, OPENAI_API_KEY, GEMINI_API_KEY
    from backend.research_service import research_crawler
    from backend.ai_service import ai_service
    from backend.export_service import export_service
    from backend.rpa_engine import hwp_rpa_engine
    from backend.git_service import git_service
    from backend.db import get_db
except ImportError:
    from config import set_api_keys, OPENAI_API_KEY, GEMINI_API_KEY
    from research_service import research_crawler
    from ai_service import ai_service
    from export_service import export_service
    from rpa_engine import hwp_rpa_engine
    from git_service import git_service
    from db import get_db

app = FastAPI(title="AutoSubjectr - Workbook Auto Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

class ApiKeysRequest(BaseModel):
    openai_api_key: Optional[str] = ""
    gemini_api_key: Optional[str] = ""

class ResearchRequest(BaseModel):
    major_topic: str
    sub_topic: str

class TopicItem(BaseModel):
    major_topic: str
    sub_topic: str
    subtypes: List[str] = []

class GenerateRequest(BaseModel):
    school_level: str = "중학교"
    grade: str = "2학년"
    semester: str = "1학기"
    topic_list: List[TopicItem]
    model_name: str = "GPT-4o"
    temperature: float = 0.7
    custom_prompt: Optional[str] = ""
    count_per_topic: int = 3
    run_rpa: bool = False

@app.get("/")
def read_root():
    return {
        "status": "ok", 
        "message": "AutoSubjectr Backend API is running flawlessly.",
        "openai_key_configured": bool(OPENAI_API_KEY),
        "gemini_key_configured": bool(GEMINI_API_KEY)
    }

@app.post("/api/config/keys")
def update_api_keys(req: ApiKeysRequest):
    set_api_keys(req.openai_api_key, req.gemini_api_key)
    return {
        "status": "success", 
        "message": "AI API Key가 성공적으로 업데이트되었습니다."
    }

@app.post("/api/research")
def research_subtypes(req: ResearchRequest):
    try:
        subtypes = research_crawler.search_subtypes(req.major_topic, req.sub_topic)
        return {"subtypes": subtypes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def generate_workbook(req: GenerateRequest, background_tasks: BackgroundTasks):
    if not req.topic_list:
        raise HTTPException(status_code=400, detail="최소 하나 이상의 단원을 추가해야 합니다.")

    await manager.broadcast({
        "type": "log", 
        "message": f"📚 [{req.school_level} {req.grade} {req.semester}] 총 {len(req.topic_list)}개 단원 문제집 일괄 생성 시작..."
    })
    
    # 1. 다중 단원 문항 및 렌더링 이미지 생성
    raw_topic_list = [t.dict() for t in req.topic_list]
    questions = ai_service.generate_questions_for_topics(
        req.school_level,
        req.grade,
        req.semester,
        raw_topic_list,
        req.count_per_topic,
        req.custom_prompt
    )
    
    # 2. Raw Data 저장 (CSV / XLSX)
    file_prefix = f"Workbook_{req.school_level}_{req.grade}_{req.semester}"
    paths = export_service.export_questions(questions, file_prefix)
    await manager.broadcast({
        "type": "log", 
        "message": f"📊 전체 문제집 Raw Data 저장 완료!\n- CSV: {paths['csv_path']}\n- XLSX: {paths['xlsx_path']}"
    })
    
    # 3. RPA 자동화 비동기 실행 (선택 시)
    if req.run_rpa:
        background_tasks.add_task(run_rpa_task, questions)

    return {
        "status": "success",
        "question_count": len(questions),
        "paths": paths,
        "questions": questions
    }

async def run_rpa_task(questions: list):
    try:
        from backend.config import IMAGES_DIR
    except ImportError:
        from config import IMAGES_DIR

    await manager.broadcast({"type": "log", "message": "🖥️ 한글(HWP) 포그라운드 모드 활성화 중..."})
    hwp_rpa_engine.bring_hwp_to_front()
    
    current_section = ""
    for idx, q in enumerate(questions, 1):
        # 단원이 변경될 때 단원 제목 타이핑
        if q["Section"] != current_section:
            current_section = q["Section"]
            await manager.broadcast({"type": "log", "message": f"📖 단원 헤더 입력: {current_section}"})
        
        await manager.broadcast({"type": "log", "message": f"✍️ [문제 {idx}/{len(questions)}] 한글 본문 타이핑 & 이미지 삽입..."})
        choices_list = [c.strip() for c in q["Choices"].split(",")]
        img_path = str(IMAGES_DIR / q['Image_File'])
        
        success = hwp_rpa_engine.type_question_into_hwp(idx, q["Question"], choices_list, img_path)
        if not success:
            await manager.broadcast({"type": "log", "message": "⚠️ 킬스위치(Ctrl+Shift+F12) 작동으로 RPA가 안전하게 중단되었습니다."})
            break
        await asyncio.sleep(0.4)
        
    await manager.broadcast({"type": "log", "message": "🎉 전체 문제집 한글(HWP) 실물 입력이 완료되었습니다!"})

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    import os
    import sys
    from pathlib import Path
    
    # 루트 디렉토리 보정
    root_dir = Path(__file__).resolve().parent.parent
    os.chdir(root_dir)
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
        
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
