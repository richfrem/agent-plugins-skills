import os
import sys
import shutil
import subprocess

class GeminiAdapter:
    def __init__(self):
        self.name = "gemini"
        self.default_model = "gemini-3-flash-preview"
        # Pin version to avoid supply-chain drift of @latest
        self.npx_package = "@google/gemini-cli@1.1.0"

    def _inject_darwin_paths(self):
        if sys.platform == "darwin":
            if os.path.exists("/opt/homebrew/bin") and "/opt/homebrew/bin" not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ.get('PATH', '')}"

    def heartbeat(self) -> bool:
        self._inject_darwin_paths()
        binary = shutil.which("gemini")
        if not binary:
            if not shutil.which("npx"):
                return False
        
        test_cmd = [binary] if binary else ["npx", "--yes", self.npx_package]
        test_cmd.extend(["-m", self.default_model, "-p", "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."])
        
        try:
            res = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            return "HEARTBEAT_OK" in res.stdout or res.returncode == 0
        except Exception:
            return False

    def build_command(self, prompt_content: str, model: str, isolated: bool) -> list[str]:
        self._inject_darwin_paths()
        binary = shutil.which("gemini")
        
        cmd_args = []
        # SECURE BY DEFAULT: Only pass --yolo if isolated is False (elevated access approved)
        if not isolated:
            cmd_args.append("--yolo")

        m = model or self.default_model
        
        if binary:
            return [binary] + cmd_args + ["-m", m, "-p", prompt_content]
        elif shutil.which("npx"):
            return ["npx", "--yes", self.npx_package] + cmd_args + ["-m", m, "-p", prompt_content]
        else:
            raise RuntimeError("Neither 'gemini' nor 'npx' executable found in PATH.")
