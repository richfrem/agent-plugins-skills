"""
Purpose:
    Adapter for the Claude Code CLI backend, providing heartbeat checks and
    command construction for cli-agents dispatch.

Key Input Dependencies:
    - claude CLI binary on PATH
"""
import shutil
import subprocess

class ClaudeAdapter:
    """Adapter for invoking the Claude Code CLI."""

    def __init__(self):
        """Initialize with the adapter name and default model."""
        self.name = "claude"
        self.default_model = "haiku-4.5"

    def heartbeat(self) -> bool:
        """Return True if the claude CLI is installed and responds to a heartbeat prompt."""
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
        """Build the claude CLI command list for the given prompt and model."""
        # Claude CLI does not have --yolo/tools flag.
        return ["claude", "--model", model or self.default_model, "-p", prompt_content]
