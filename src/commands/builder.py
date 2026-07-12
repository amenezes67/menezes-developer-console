import subprocess
import sys


def run():

    task = sys.argv[1] if len(sys.argv) > 1 else ""

    print("=" * 60)
    print("MDC Builder")
    print("=" * 60)

    subprocess.run(
        [
            "python",
            "src/modules/ai/builder/builder.py",
            task,
        ]
    )


if __name__ == "__main__":
    run()