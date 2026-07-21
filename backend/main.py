from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio

from backend.research_service import research_crawler
from backend.ai_service import ai_service
from backend.export_service import export_service
from backend.rpa_engine import hwp_rpa_engine
from backend.git_service import git_service
from backend.db import get_db

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

class ResearchRequest(BaseModel):
    major_topic: str
    sub_topic: str

class GenerateRequest(BaseModel):
    major_topic: str
    sub_topic: str
    selected_subtypes: List[str]
    model_name: str = "GPT-4o"
    temperature: float = 0.7
    custom_prompt: Optional[str] = ""
    count: int = 5
    run_rpa: bool = False

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AutoSubjectr Backend API is running."}

@app.post("/api/research")
def research_subtypes(req: ResearchRequest):
    subtypes = research_crawler.search_subtypes(req.major_topic, req.sub_topic)
    return {"subtypes": subtypes}

@app.post("/api/generate")
async def generate_workbook(req: GenerateRequest, background_tasks: BackgroundTasks):
    await manager.broadcast({"type": "log", "message": f"🤖 AI 문항 생성 시작... (단원: {req.major_topic} > {req.sub_topic})"})
    
    # 1. 문항 및 렌더링 이미지 생성
    questions = ai_service.generate_questions(
        req.major_topic,
        req.sub_topic,
        req.selected_subtypes,
        req.count,
        req.custom_prompt
    )
    
    # 2. Raw Data 저장 (CSV / XLSX)
    file_prefix = f"prob_{req.sub_topic}"
    paths = export_service.export_questions(questions, file_prefix)
    await manager.broadcast({
        "type": "log", 
        "message": f"📊 데이터 저장 완료!\n- CSV: {paths['csv_path']}\n- XLSX: {paths['xlsx_path']}"
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
    await manager.broadcast({"type": "log", "message": "🖥️ 한글(HWP) 로컬 워드프로세서 포그라운드 활성화 중..."})
    hwp_rpa_engine.bring_hwp_to_front()
    
    for idx, q in enumerate(questions, 1):
        await manager.broadcast({"type": "log", "message": f"✍️ [문제 {idx}/{len(questions)}] 한글 문서에 타이핑 & 이미지 삽입 중..."})
        choices_list = [c.strip() for c in q["Choices"].split(",")]
        img_path = f"C:\\Users\\WDAGUtilityAccount\\Desktop\\test\\Workbook_Output\\Images\\{q['Image_File']}"
        
        success = hwp_rpa_engine.type_question_into_hwp(idx, q["Question"], choices_list, img_path)
        if not success:
            await manager.broadcast({"type": "log", "message": "⚠️ 킬스위치 작동으로 인해 한글 RPA 작업이 중단되었습니다."})
            break
        await asyncio.sleep(0.5)
        
    await manager.broadcast({"type": "log", "message": "✅ 한글(HWP) 입력 작업이 완료되었습니다!"})

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
