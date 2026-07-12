def show_main_menu() -> str:
    print()
    print("1 - Proyectos")
    print("2 - Publicaciones")
    print("3 - Ingeniería")
    print("4 - IA / TESS")
    print("5 - Utilidades")
    print()
    print("0 - Salir")

    option = input("\nSeleccione una opción: ").strip()

    if option not in {"0", "1", "2", "3", "4", "5"}:
        print("\nOpción inválida.")
        input("\nPresione ENTER para continuar...")
        return ""

    return option