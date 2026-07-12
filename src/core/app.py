from datetime import datetime

from src.core.menu import show_main_menu
from src.core.version import APP_BUILD, APP_NAME, APP_STAGE, APP_VERSION


def print_header() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print()
    print("=" * 60)
    print(f"{APP_NAME:^60}")
    print("=" * 60)
    print(f"Version : {APP_VERSION}")
    print(f"Build   : {APP_BUILD}")
    print(f"Stage   : {APP_STAGE}")
    print(f"Local   : {now}")
    print("=" * 60)


def main() -> None:
    while True:
        print_header()
        option = show_main_menu()

        if option == "0":
            print("\nHasta luego.")
            break

        print(f"\nOpción seleccionada: {option}")
        input("\nPresione ENTER para continuar...")
