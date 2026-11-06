"""Shared fixtures: a fake `claude` worker (REAL subprocess, MOCKED model) whose behavior is driven by markers in its brief."""
import json, os, sys, tempfile
from pathlib import Path

S = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(S / "orchestrating-agent-work/scripts"))
sys.path.insert(0, str(S / "evaluating-agent-outcomes/scripts"))
sys.path.insert(0, str(S / "cli-agent/scripts"))
import work_loop as wl  # noqa: E402

WORKER = r'''#!%(py)s
import sys, re, os, time, subprocess, json
args = sys.argv[1:]
if "--version" in args:
    print("fixture 1"); sys.exit(0)
brief = " ".join(args)
if "--output-format" in args and "stream-json" in args:      # context probe: report the init event honestly
    model = args[args.index("--model") + 1]
    print(json.dumps({"type": "system", "subtype": "init", "cwd": os.getcwd(), "model": model, "tools": [], "slash_commands": [], "skills": [], "mcp_servers": []}))
    sys.exit(0)
m = re.search(r"CREATE:(\S+)", brief)
if "SLEEP:" in brief:
    time.sleep(float(re.search(r"SLEEP:([\d.]+)", brief).group(1)))
if "SPAWN_CHILD" in brief:
    c = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    open(os.environ.get("CHILD_PID_FILE", os.devnull), "w").write(str(c.pid))
    print("partial-output-marker", flush=True); time.sleep(60)
if "FAIL_FIRST" in brief and "Repair required" not in brief:
    print("worker failed on purpose"); sys.exit(1)
if "TOKENS_ONCE" in brief and "Repair required" not in brief:
    print("tokens used\n1,234")
if m:
    open(m.group(1), "w").write("print('hello')\n")
print("done")
'''


def make_repo(tmp=None):
    repo = Path(tmp or tempfile.mkdtemp()); (repo / ".git").mkdir(exist_ok=True)
    tools = Path(tempfile.mkdtemp()); w = tools / "claude"
    w.write_text(WORKER % {"py": sys.executable}); w.chmod(0o755)
    return repo, tools, w


def contract(wid, fname="hello.py", goal="create hello script", **budget):
    b = {"max_attempts": 3}; b.update(budget)
    return {"id": wid, "type": "task", "goal": goal, "scope": {"paths": [fname]},
            "acceptance": [{"id": "A1", "text": "script prints hello", "check": {"kind": "command", "argv": [sys.executable, fname], "expect_stdout_contains": ["hello"]}}],
            "failure_conditions": [{"id": "F1", "text": "error marker", "check": {"kind": "file_exists", "path": "ERROR.txt"}}],
            "budget": b, "authorization": {"may_merge": False}}


def put(repo, c, name="c.json"):
    p = Path(repo) / name; p.write_text(json.dumps(c)); return p
