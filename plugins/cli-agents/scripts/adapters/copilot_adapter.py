import sys
import shutil
import subprocess

class CopilotAdapter:
    def __init__(self):
        self.name = "copilot"
        self.default_model = "gpt-5-mini"

    def heartbeat(self) -> bool:
        if not shutil.which("copilot"):
            return False
        try:
            res = subprocess.run(
                ["copilot", "--model", self.default_model, "-p", "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Accept return code 0 or successful string match
            return "HEARTBEAT_OK" in res.stdout or res.returncode == 0
        except Exception:
            return False

    def build_command(self, prompt_path: str, model: str, isolated: bool) -> list[str]:
        m = model or self.default_model
        cmd_args = []
        # SECURE BY DEFAULT: Only pass --yolo if isolated is False (elevated access approved)
        if not isolated:
            cmd_args.append("--yolo")
            
        if sys.platform == "win32":
            return ["powershell", "-NoProfile", "-Command", f'copilot {" ".join(cmd_args)} --model {m} -p (Get-Content -Raw "{prompt_path}")']
        else:
            return ["copilot"] + cmd_args + ["--model", m, "-p", f"@{prompt_path}"]
