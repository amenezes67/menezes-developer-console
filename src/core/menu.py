def show_main_menu() -> str:
    print()
    print("1 - Proyectos")
    print("2 - Publicaciones")
    print("3 - Ingeniería")
    print("4 - IA / TESS")
    print("5 - Utilidades")
    print()
    print("0 - Salir")

    return input("\nSeleccione una opción: ").strip()
