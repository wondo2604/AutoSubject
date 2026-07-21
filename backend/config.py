import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# sys.path 호환 처리
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# .env 로드
load_dotenv()

BASE_DIR = PROJECT_ROOT

# 출력 경로
OUTPUT_BASE_DIR = Path(os.getenv("OUTPUT_BASE_DIR", r"C:\Users\WDAGUtilityAccount\Desktop\test\Workbook_Output"))
DATA_DIR = OUTPUT_BASE_DIR / "Data"
IMAGES_DIR = OUTPUT_BASE_DIR / "Images"

# 자동 디렉토리 생성
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def set_api_keys(openai_key: str = None, gemini_key: str = None):
    global OPENAI_API_KEY, GEMINI_API_KEY
    if openai_key is not None:
        OPENAI_API_KEY = openai_key
        os.environ["OPENAI_API_KEY"] = openai_key
    if gemini_key is not None:
        GEMINI_API_KEY = gemini_key
        os.environ["GEMINI_API_KEY"] = gemini_key

# Git Config
GIT_USER_NAME = os.getenv("GIT_USER_NAME", "wondo")
GIT_USER_EMAIL = os.getenv("GIT_USER_EMAIL", "wondo1@outlook.kr")
GIT_REMOTE_URL = os.getenv("GIT_REMOTE_URL", "")
GIT_EXE = r"C:\Program Files\Git\cmd\git.exe"
