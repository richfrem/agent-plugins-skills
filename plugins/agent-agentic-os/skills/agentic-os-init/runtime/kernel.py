#!/usr/bin/env python3
"""
Agentic OS - Kernel Controller
Provides atomic file locks, strict JSON schema event emitting, and state management.
"""
import os
import sys
import json
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

KERNEL_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / "context"
EVENTS_FILE = KERNEL_DIR / "events.jsonl"
LOCKS_DIR = KERNEL_DIR / ".locks"
STATE_FILE = KERNEL_DIR / "os-state.json"
AGENTS_FILE = KERNEL_DIR / "agents.json"
EVENTS_MAX_SIZE = 10 * 1024 * 1024  # 10MB

def validate_agent(agent_name):
    if not AGENTS_FILE.exists():
        return False # Fail closed
    try:
        with open(AGENTS_FILE, "r") as f:
            registry = json.load(f)
            if agent_name in registry.get("permitted_agents", []):
                return True
            print(f"Error: Unregistered agent spoofing detected: {agent_name}", file=sys.stderr)
            return False
    except json.JSONDecodeError:
        return True # Fallback if corrupted

def acquire_lock(lock_name):
    """Acquires a lock atomically using os.mkdir."""
    lock_path = LOCKS_DIR / f"{lock_name}.lock"
    os.makedirs(LOCKS_DIR, exist_ok=True)
    
    # Check for stale lock first
    if lock_path.exists():
        age = time.time() - lock_path.stat().st_mtime
        if age > 1800: # 30 mins
            try:
                os.rmdir(lock_path)
                print(f"[Kernel] Cleared stale lock: {lock_name}")
            except OSError:
                pass
        else:
            print(f"[Kernel] Failed to acquire lock '{lock_name}' (locked by another process)", file=sys.stderr)
            sys.exit(1)
            
    try:
        os.mkdir(lock_path)
        print(f"[Kernel] Lock acquired: {lock_name}")
    except FileExistsError:
        print(f"[Kernel] Race condition check failed. Lock '{lock_name}' already exists.", file=sys.stderr)
        sys.exit(1)

def release_lock(lock_name):
    """Releases a lock."""
    lock_path = LOCKS_DIR / f"{lock_name}.lock"
    try:
        os.rmdir(lock_path)
        print(f"[Kernel] Lock released: {lock_name}")
    except OSError:
        pass # Already gone or not ours

def rotate_events():
    """Rotates events.jsonl if > 10MB."""
    if not EVENTS_FILE.exists() or EVENTS_FILE.stat().st_size <= EVENTS_MAX_SIZE:
        return
        
    archive_dir = KERNEL_DIR / "events-archive"
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_file = archive_dir / f"events-{timestamp}.jsonl"
    
    try:
        # We need an atomic lock on the events file itself to safely rotate it.
        # This is internal to the kernel.
        events_lock = LOCKS_DIR / "events_rotate.lock"
        os.mkdir(events_lock)
        
        try:
            # Re-check size after acquiring lock
            if EVENTS_FILE.exists() and EVENTS_FILE.stat().st_size > EVENTS_MAX_SIZE:
                os.rename(EVENTS_FILE, archive_file)
                # Inform active agents that a rotation just occurred so they don't think the bus is dead
                maint_event = {
                    "time": datetime.now().isoformat() + "Z",
                    "agent": "kernel",
                    "type": "system_maintenance",
                    "action": "event_rotation",
                    "status": "success",
                    "summary": f"Rotated events to {archive_file.name}"
                }
                with open(EVENTS_FILE, "w", encoding="utf-8") as f:
                    f.write(json.dumps(maint_event) + "\n")
                print(f"[Kernel] Rotated events.jsonl to {archive_file}")
        finally:
            os.rmdir(events_lock)
    except FileExistsError:
        pass # Another process is already rotating it

def emit_event(agent, type_, action, status=None, summary=None, results=None):
    if not validate_agent(agent):
        sys.exit(1)
        
    rotate_events()
    
    event = {
        "time": datetime.now().isoformat() + "Z",
        "agent": agent,
        "type": type_,
        "action": action
    }
    if status is not None:
        event["status"] = status
    if summary is not None:
        event["summary"] = summary
    if results is not None:
        try:
            event["results"] = json.loads(results) if isinstance(results, str) else results
        except json.JSONDecodeError:
            event["results"] = results
        
    try:
        # Use an atomic lock to append to events.jsonl
        events_write_lock = LOCKS_DIR / "events_write.lock"
        # Simple spinlock with collision jitter
        retries = 150
        while retries > 0:
            try:
                os.mkdir(events_write_lock)
                break
            except FileExistsError:
                if time.time() - events_write_lock.stat().st_mtime > 20:
                   try: os.rmdir(events_write_lock) 
                   except OSError: pass
                time.sleep(random.uniform(0.1, 0.3))
                retries -= 1
                
        if retries == 0:
            print("[Kernel] Failed to acquire events.jsonl write lock", file=sys.stderr)
            sys.exit(1)
            
        with open(EVENTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
            
        os.rmdir(events_write_lock)
        print(f"[Kernel] Event emitted ({type_}: {action})")
    except Exception as e:
        print(f"[Kernel] Event emit failed: {e}", file=sys.stderr)

def state_update(key, value):
    """Updates a single key in the os-state.json file with a lock."""
    state_lock = LOCKS_DIR / "state_write.lock"
    # Simple spinlock with collision jitter
    retries = 150
    while retries > 0:
        try:
            os.makedirs(LOCKS_DIR, exist_ok=True)
            os.mkdir(state_lock)
            break
        except FileExistsError:
            if time.time() - state_lock.stat().st_mtime > 20:
               try: os.rmdir(state_lock) 
               except OSError: pass
            time.sleep(random.uniform(0.1, 0.3))
            retries -= 1
            
    if retries == 0:
        print("[Kernel] Failed to acquire os-state.json write lock", file=sys.stderr)
        sys.exit(1)
        
    try:
        state = {}
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    loaded_state = json.load(f)
                    if isinstance(loaded_state, dict):
                        state = loaded_state
            except json.JSONDecodeError:
                pass
                
        # Parse value if it is valid JSON
        try:
            val_parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            val_parsed = value
            
        state[key] = val_parsed
        
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
            
        print(f"[Kernel] State updated: {key}")
    finally:
        os.rmdir(state_lock)

def main():
    parser = argparse.ArgumentParser(description="Agentic OS Kernel Controller")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # acquire_lock
    lock_parser = subparsers.add_parser("acquire_lock")
    lock_parser.add_argument("name")
    
    # release_lock
    unlock_parser = subparsers.add_parser("release_lock")
    unlock_parser.add_argument("name")
    
    # emit_event
    event_parser = subparsers.add_parser("emit_event")
    event_parser.add_argument("--agent", required=True)
    event_parser.add_argument("--type", required=True, choices=["intent", "result", "error", "learning", "memory_promotion", "skill_update", "agent_start", "agent_stop", "metric"])
    event_parser.add_argument("--action", required=True)
    event_parser.add_argument("--status", choices=["success", "fail"])
    event_parser.add_argument("--summary")
    event_parser.add_argument("--results")
    
    # state_update
    state_parser = subparsers.add_parser("state_update")
    state_parser.add_argument("key")
    state_parser.add_argument("value")
    
    args = parser.parse_args()
    
    if args.command == "acquire_lock":
        acquire_lock(args.name)
    elif args.command == "release_lock":
        release_lock(args.name)
    elif args.command == "emit_event":
        emit_event(args.agent, args.type, args.action, args.status, args.summary, args.results)
    elif args.command == "state_update":
        state_update(args.key, args.value)

if __name__ == "__main__":
    main()
