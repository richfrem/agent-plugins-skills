#!/usr/bin/env python3
"""
find_polluter.py
=====================================

Purpose:
    Bisection helper that iterates test files and executes `npm test` on each
    to identify which individual test is first responsible for creating an
    unwanted filesystem artifact (file, directory, or polluted state).

Layer: Investigate

Usage:
    python3 find_polluter.py <file_or_dir_to_check> <test_pattern>
    python3 find_polluter.py '.git' 'src/**/*.test.ts'
"""
import sys
import os
import glob
import subprocess


# Entry point: parse CLI args and run sequential bisection across test files
def main() -> None:
    """
    Run bisection search over test files to find the pollution source.

    Reads positional arguments from sys.argv (file_to_check, test_pattern),
    iterates every matching test file in sorted order, and reports the first
    file that causes the unwanted artifact to appear.

    Raises:
        SystemExit: Code 1 on bad args or polluter found; code 0 when clean.
    """
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <file_to_check> <test_pattern>")
        print(f"Example: {sys.argv[0]} '.git' 'src/**/*.test.ts'")
        sys.exit(1)

    pollution_check = sys.argv[1]
    test_pattern = sys.argv[2]

    print(f"Searching for test that creates: {pollution_check}")
    print(f"Test pattern: {test_pattern}")
    print()

    test_files = sorted(glob.glob(test_pattern, recursive=True))
    total = len(test_files)

    print(f"Found {total} test files")
    print()

    for count, test_file in enumerate(test_files, 1):
        if os.path.exists(pollution_check):
            print(f"WARNING: Pollution already exists before test {count}/{total}")
            print(f"   Skipping: {test_file}")
            continue

        print(f"[{count}/{total}] Testing: {test_file}")

        subprocess.run(
            ["npm", "test", test_file],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if os.path.exists(pollution_check):
            print()
            print("FOUND POLLUTER!")
            print(f"   Test: {test_file}")
            print(f"   Created: {pollution_check}")
            print()
            print("Pollution details:")
            subprocess.run(["ls", "-la", pollution_check])
            print()
            print("To investigate:")
            print(f"  npm test {test_file}    # Run just this test")
            print(f"  cat {test_file}         # Review test code")
            sys.exit(1)

    print()
    print("No polluter found - all tests clean!")
    sys.exit(0)


if __name__ == "__main__":
    main()
