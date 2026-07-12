"""
Builder AI integration
Menezes Developer Console
"""

from pathlib import Path


def run():

    root = Path.cwd()

    print("=" * 60)
    print("MDC AI Builder")
    print("=" * 60)
    print()

    print("Current project:")
    print(root)
    print()

    if (root / ".git").exists():
        print("Git repository : OK")
    else:
        print("ERROR: not inside a git repository")
        return

    if (root / "index.html").exists():
        print("Website project : YES")
    else:
        print("Website project : NO")

    print()
    print("Ready.")
if __name__ == "__main__":
    run()