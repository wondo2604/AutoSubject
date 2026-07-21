import subprocess
import os
from pathlib import Path
from backend.config import BASE_DIR, GIT_EXE, GIT_USER_NAME, GIT_USER_EMAIL, GIT_REMOTE_URL

class GitService:
    def __init__(self, repo_dir: Path = BASE_DIR):
        self.repo_dir = repo_dir
        self.git_exe = GIT_EXE if os.path.exists(GIT_EXE) else "git"

    def run_git_cmd(self, args: list):
        cmd = [self.git_exe] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip() or e.stdout.strip()

    def commit_and_push(self, summary: str, details: list = None) -> tuple[bool, str]:
        """
        사용자 커밋 작성 규칙 준수:
        첫째 줄: 요약
        이후: 구체적 내용 리스트
        """
        message_lines = [summary]
        if details:
            message_lines.append("")
            for item in details:
                message_lines.append(f"- {item}")
        
        full_message = "\n".join(message_lines)

        # 1. git add
        success, out = self.run_git_cmd(["add", "."])
        if not success:
            return False, f"Git add 실패: {out}"

        # 2. git commit
        success, out = self.run_git_cmd(["commit", "-m", full_message])
        if not success and "nothing to commit" in out:
            return True, "변경 사항이 없어 커밋하지 않았습니다."
        elif not success:
            return False, f"Git commit 실패: {out}"

        # 3. git push origin master / main
        success, push_out = self.run_git_cmd(["push", "origin", "HEAD:main"])
        if not success:
            # fallback to master
            success, push_out = self.run_git_cmd(["push", "origin", "HEAD:master"])

        if success:
            return True, f"Git 커밋 및 푸시 성공!\n{full_message}"
        else:
            return False, f"Git push 실패: {push_out}"

git_service = GitService()
