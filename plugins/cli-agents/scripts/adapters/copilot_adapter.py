"""
Purpose:
    Adapter for the GitHub Copilot CLI backend, providing heartbeat checks and
    command construction (including cross-platform --yolo/isolation handling)
    for cli-agents dispatch.

Key Input Dependencies:
    - copilot CLI binary on PATH
"""
import sys
import shutil
import subprocess

class CopilotAdapter:
    """Adapter for invoking the GitHub Copilot CLI."""

    def __init__(self):
        """Initialize with the adapter name and default model."""
        self.name = "copilot"
        self.default_model = "gpt-5-mini"

    def heartbeat(self) -> bool:
        """Return True if the copilot CLI is installed and responds to a heartbeat prompt."""
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
        """Build the copilot CLI command list, handling --yolo and Windows/POSIX differences."""
        m = model or self.default_model
        cmd_args = []
        # SECURE BY DEFAULT: Only pass --yolo if isolated is False (elevated access approved)
        if not isolated:
            cmd_args.append("--yolo")
            
        if sys.platform == "win32":
            return ["powershell", "-NoProfile", "-Command", f'copilot {" ".join(cmd_args)} --model {m} -p (Get-Content -Raw "{prompt_path}")']
        else:
            return ["copilot"] + cmd_args + ["--model", m, "-p", f"@{prompt_path}"]
