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

# 출력 경로 설정 (모든 윈도우 사용자 계정 환경 및 권한 문제 자동 대응)
# 1순위: .env 설정 경로 (유효한 경우)
# 2순위: 현재 사용자 바탕화면 (Path.home() / "Desktop" / "Workbook_Output")
# 3순위: 프로젝트 루트 폴더 (PROJECT_ROOT / "Workbook_Output")

env_out = os.getenv("OUTPUT_BASE_DIR", "").strip()

def resolve_output_dir():
    candidates = []
    if env_out and not env_out.startswith(r"C:\Users\WDAGUtilityAccount"):
        candidates.append(Path(env_out))
    
    # 사용자 홈 바탕화면 경로
    try:
        desktop_dir = Path.home() / "Desktop" / "Workbook_Output"
        candidates.append(desktop_dir)
    except Exception:
        pass
        
    # 프로젝트 내 폴더 (최종 안전 보장 경로)
    candidates.append(PROJECT_ROOT / "Workbook_Output")

    for cand in candidates:
        try:
            data_p = cand / "Data"
            img_p = cand / "Images"
            data_p.mkdir(parents=True, exist_ok=True)
            img_p.mkdir(parents=True, exist_ok=True)
            return cand, data_p, img_p
        except (PermissionError, OSError) as e:
            print(f"⚠️ Warning: {cand} 디렉터리 생성 권한 없음 ({e}). 다음 디렉터리로 전환합니다.")
            continue
            
    # 최종 fallback: 상대 경로
    fallback = PROJECT_ROOT / "Workbook_Output"
    (fallback / "Data").mkdir(parents=True, exist_ok=True)
    (fallback / "Images").mkdir(parents=True, exist_ok=True)
    return fallback, fallback / "Data", fallback / "Images"

OUTPUT_BASE_DIR, DATA_DIR, IMAGES_DIR = resolve_output_dir()

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
