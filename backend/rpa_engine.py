import time
import pyperclip
import pyautogui
import os
from pathlib import Path

try:
    from backend.kill_switch import kill_switch_manager
except ImportError:
    from kill_switch import kill_switch_manager

class HwpRpaEngine:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3

    def bring_hwp_to_front(self) -> bool:
        """
        현재 윈도우 OS에서 실행 중인 '한글' (HWP) 프로세스 창을 포그라운드로 복원/최상단 활성화
        """
        try:
            import pywinauto
            app = pywinauto.Application().connect(title_re=".*한글.*|.*HWP.*|.*Hnc.*", timeout=2)
            win = app.top_window()
            win.set_focus()
            time.sleep(0.5)
            return True
        except Exception:
            # win32gui fallback
            try:
                import win32gui, win32con
                def enum_windows_callback(hwnd, extra):
                    title = win32gui.GetWindowText(hwnd)
                    if "한글" in title or "HWP" in title:
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        win32gui.SetForegroundWindow(hwnd)
                win32gui.EnumWindows(enum_windows_callback, None)
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"HWP Window Focus Error: {e}")
                return False

    def type_question_into_hwp(self, q_num: int, q_text: str, choices: list[str], image_path: str = None) -> bool:
        """
        한글 문서 내에 텍스트 문제 및 이미지를 타이핑/삽입
        """
        if kill_switch_manager.is_killed():
            print("Kill-Switch가 작동하여 RPA를 중단합니다.")
            return False

        # 1. 텍스트 클립보드 복사 & 붙여넣기
        full_text = f"[문제 {q_num}] {q_text}\n"
        if choices:
            for idx, choice in enumerate(choices, 1):
                full_text += f"  {idx}. {choice}\n"
        
        pyperclip.copy(full_text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)

        # 2. 이미지 파일이 존재하는 경우 한글 이미지 삽입 단축키 (Ctrl + N, I)
        if image_path and os.path.exists(image_path):
            pyautogui.hotkey('ctrl', 'n')
            pyautogui.press('i')
            time.sleep(0.5)
            
            # 파일 탐색기 창에 경로 입력 후 Enter
            pyperclip.copy(str(Path(image_path).resolve()))
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.3)
            pyautogui.press('enter')
            time.sleep(0.5)

        # 3. 한 문제 완료 후 엔터 3회 포맷팅
        pyautogui.press('enter', presses=3, interval=0.1)
        return True

hwp_rpa_engine = HwpRpaEngine()
