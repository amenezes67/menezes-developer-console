import shutil
import subprocess
from pathlib import Path


WEB_PROJECT_PATH = Path(r"X:\amenezes67\menezes-pro")


def open_web_project() -> None:
    if not WEB_PROJECT_PATH.exists():
        print(f"\nNo existe la carpeta:\n{WEB_PROJECT_PATH}")
        input("\nPresione ENTER para continuar...")
        return

    code_command = shutil.which("code")

    if code_command:
        subprocess.Popen([code_command, str(WEB_PROJECT_PATH)])
        print("\nProyecto web abierto en VS Code.")
        return

    possible_paths = [
        Path.home() / "AppData/Local/Programs/Microsoft VS Code/Code.exe",
        Path(r"C:\Program Files\Microsoft VS Code\Code.exe"),
    ]

    for executable in possible_paths:
        if executable.exists():
            subprocess.Popen([str(executable), str(WEB_PROJECT_PATH)])
            print("\nProyecto web abierto en VS Code.")
            return

    print("\nVS Code no fue encontrado.")
    input("\nPresione ENTER para continuar...")
