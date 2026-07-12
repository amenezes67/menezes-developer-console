#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys


def git(cmd):
    return subprocess.check_output(
        ["git"] + cmd,
        text=True
    ).strip()


def detect_repo():
    return Path(git(["rev-parse", "--show-toplevel"]))


def detect_branch():
    return git(["branch", "--show-current"])


def main():

    task = sys.argv[1] if len(sys.argv) > 1 else "none"

    repo = detect_repo()

    print("=" * 60)
    print("MENEZES DEVELOPER CONSOLE")
    print("=" * 60)
    print()

    print(f"Project : {repo.name}")
    print(f"Path    : {repo}")
    print(f"Branch  : {detect_branch()}")
    print(f"Task    : {task}")

    print()

    if repo.name != "menezes-pro":
        print("WARNING: not inside menezes-pro")

    print()
    print("READY")


if __name__ == "__main__":
    main()