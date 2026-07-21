import os
import sys
from pathlib import Path

# 작업 디렉토리를 프로젝트 루트로 강력 고정
ROOT_DIR = Path(__file__).resolve().parent
os.chdir(ROOT_DIR)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(ROOT_DIR / "backend") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "backend"))

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 AutoSubjectr 백엔드 서버를 시작합니다... (Root: {ROOT_DIR})")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
