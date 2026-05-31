import shutil
import subprocess

class ClaudeAdapter:
    def __init__(self):
        self.name = "claude"
        self.default_model = "haiku-4.5"

    def heartbeat(self) -> bool:
        if not shutil.which("claude"):
            return False
        # Zero-shot verification
        try:
            res = subprocess.run(
                ["claude", "-p", "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."],
                capture_output=True,
                text=True,
                timeout=10
            )
            return "HEARTBEAT_OK" in res.stdout or res.returncode == 0
        except Exception:
            return False

    def build_command(self, prompt_content: str, model: str, isolated: bool) -> list[str]:
        # Claude CLI does not have --yolo/tools flag.
        return ["claude", "--model", model or self.default_model, "-p", prompt_content]
