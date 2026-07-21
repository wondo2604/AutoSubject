import keyboard
import threading

class KillSwitchManager:
    def __init__(self):
        self._killed = False
        self._listener_thread = None

    def start_listener(self):
        self._killed = False
        def on_triggered():
            print("\n[⚠️ KILL-SWITCH DETECTED] Ctrl+Shift+F12 가 입력되어 모든 물리 제어를 즉시 중단합니다!")
            self._killed = True

        try:
            keyboard.add_hotkey('ctrl+shift+f12', on_triggered)
        except Exception as e:
            print(f"Kill-switch hotkey registration failed: {e}")

    def is_killed(self) -> bool:
        return self._killed

    def reset(self):
        self._killed = False

kill_switch_manager = KillSwitchManager()
kill_switch_manager.start_listener()
