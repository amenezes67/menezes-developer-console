#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 MENEZES DEVELOPER CONSOLE
-------------------------------------------------------------------------------

 Version............. 3.01
 Base Version........ 3.00
 Build............... 2026-07-11
 Stage............... DEVELOPMENT

 CHANGELOG
 ----------
 3.01
 - Renamed application to Menezes Developer Console.
 - Added version metadata.
 - Functional behavior unchanged.

===============================================================================
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Sequence

APP_NAME = "MENEZES DEVELOPER CONSOLE"
APP_VERSION = "3.01"
APP_BUILD = "2026-07-11"
APP_STAGE = "DEVELOPMENT"

APP_DIR = Path(__file__).resolve().parent
CONFIG_FILE = APP_DIR / "config.json"
LOG_DIR = APP_DIR / "logs"
LOG_FILE = LOG_DIR / "github-manager.log"


class AppError(RuntimeError):
    pass


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise AppError(f"No se encontró:\n{CONFIG_FILE}")
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise AppError(f"No se pudo leer config.json: {exc}") from exc
    if not data.get("projects"):
        raise AppError("config.json no contiene proyectos.")
    return data


CONFIG = load_config()
PROJECT = None


def project_value(key: str, default=""):
    return PROJECT.get(key, default) if PROJECT else default


def repo_path() -> Path:
    return Path(project_value("repository_path"))


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"[{stamp}] {message}\n")


def run_git(
    args: Sequence[str],
    *,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    cmd = ["git", *args]
    result = subprocess.run(
        cmd,
        cwd=repo_path(),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
        shell=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise AppError(
            f"Falló el comando:\n  {' '.join(cmd)}"
            + (f"\n\n{detail}" if detail else "")
        )
    return result


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    input("\nPresione ENTER para continuar...")


def validate_environment() -> None:
    if shutil.which("git") is None:
        raise AppError("Git no está instalado o no está disponible en PATH.")
    repo = repo_path()
    if not repo.exists():
        raise AppError(f"No existe la carpeta del repositorio:\n{repo}")
    if not (repo / ".git").exists():
        raise AppError(f"No parece ser un repositorio Git:\n{repo}")


def current_branch() -> str:
    return run_git(["branch", "--show-current"], capture=True).stdout.strip() or "(sin rama)"


def short_status() -> str:
    return run_git(["status", "--short"], capture=True).stdout.strip()


def last_commit(branch: str | None = None) -> tuple[str, str, str]:
    ref = branch or "HEAD"
    result = run_git(
        ["log", "-1", ref, "--date=format:%Y-%m-%d %H:%M", "--format=%h%x09%s%x09%ad"],
        capture=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return ("-", "(sin commits)", "")
    parts = result.stdout.strip().split("\t", 2)
    while len(parts) < 3:
        parts.append("")
    return parts[0], parts[1], parts[2]


def fetch_quiet() -> None:
    run_git(["fetch", "--quiet", project_value("remote", "origin")], check=False)


def branch_remote_sync(branch: str) -> tuple[int, int] | None:
    remote = project_value("remote", "origin")
    result = run_git(
        ["rev-list", "--left-right", "--count", f"{branch}...{remote}/{branch}"],
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        ahead, behind = map(int, result.stdout.split())
        return ahead, behind
    except ValueError:
        return None


def develop_vs_main() -> tuple[int, int] | None:
    develop = project_value("default_branch", "develop")
    main = project_value("production_branch", "main")
    result = run_git(
        ["rev-list", "--left-right", "--count", f"{main}...{develop}"],
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        main_only, develop_only = map(int, result.stdout.split())
        return main_only, develop_only
    except ValueError:
        return None


def count_files() -> int:
    result = run_git(["ls-files"], capture=True)
    return len([line for line in result.stdout.splitlines() if line.strip()])


def count_commits() -> int:
    result = run_git(["rev-list", "--count", "HEAD"], capture=True)
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def status_label() -> str:
    return "LIMPIO" if not short_status() else "CAMBIOS PENDIENTES"


def sync_label(branch: str) -> str:
    sync = branch_remote_sync(branch)
    if sync is None:
        return "SIN DATOS"
    ahead, behind = sync
    if ahead == 0 and behind == 0:
        return "SINCRONIZADO"
    pieces = []
    if ahead:
        pieces.append(f"{ahead} por subir")
    if behind:
        pieces.append(f"{behind} por bajar")
    return " / ".join(pieces)


def publication_label() -> str:
    relation = develop_vs_main()
    if relation is None:
        return "SIN DATOS"
    main_only, develop_only = relation
    if main_only == 0 and develop_only == 0:
        return "MAIN ACTUALIZADO"
    if main_only == 0 and develop_only > 0:
        return f"DEVELOP +{develop_only} commit(s) listo(s) para publicar"
    if main_only > 0 and develop_only == 0:
        return f"MAIN +{main_only} commit(s) por delante"
    return f"RAMAS DIVERGENTES: main +{main_only} / develop +{develop_only}"


def print_header() -> None:
    fetch_quiet()
    branch = current_branch()
    commit_hash, subject, date_ = last_commit()
    print("=" * 72)
    print(f"{APP_NAME:^72}")
    print(f"{('Versión ' + APP_VERSION):^72}")
    print("=" * 72)
    print(f"Proyecto      : {project_value('name')}")
    print(f"Repositorio   : {repo_path()}")
    print(f"Rama actual   : {branch}")
    print(f"Estado local  : {status_label()}")
    print(f"GitHub        : {sync_label(branch)}")
    print(f"Publicación   : {publication_label()}")
    print(f"Último commit : {commit_hash}  {subject}")
    if date_:
        print(f"Fecha         : {date_}")
    print("-" * 72)


def select_project() -> None:
    global PROJECT
    projects = CONFIG["projects"]
    default_name = CONFIG.get("default_project")

    if len(projects) == 1:
        PROJECT = projects[0]
        return

    clear()
    print("=" * 58)
    print("SELECCIONE EL PROYECTO")
    print("=" * 58)
    for idx, item in enumerate(projects, 1):
        marker = " (predeterminado)" if item.get("name") == default_name else ""
        print(f"{idx} - {item.get('name')}{marker}")
    print("0 - Salir")

    choice = input("\nOpción: ").strip()
    if choice == "0":
        raise SystemExit(0)
    try:
        PROJECT = projects[int(choice) - 1]
    except (ValueError, IndexError):
        raise AppError("Proyecto inválido.")


def ensure_clean() -> None:
    if short_status():
        raise AppError(
            "Hay cambios locales pendientes.\n"
            "Haga commit, descarte o guarde esos cambios antes de continuar."
        )


def switch_branch(branch: str) -> None:
    run_git(["switch", branch])


def pull() -> None:
    branch = current_branch()
    print(f"\nActualizando '{branch}'...")
    run_git(["pull", "--ff-only", project_value("remote", "origin"), branch])
    log(f"{project_value('name')} | PULL OK | branch={branch}")
    print("\n✓ Repositorio actualizado.")


def show_status() -> None:
    print()
    run_git(["status"])
    print("\nÚltimos commits:")
    print(run_git(["log", "--oneline", "-10"], capture=True).stdout.rstrip())


def show_project_info() -> None:
    branch = current_branch()
    commit_hash, subject, date_ = last_commit()
    print("\n" + "=" * 72)
    print("INFORMACIÓN DEL PROYECTO")
    print("=" * 72)
    print(f"Proyecto        : {project_value('name')}")
    print(f"Ruta local      : {repo_path()}")
    print(f"Remoto          : {project_value('remote', 'origin')}")
    print(f"Rama actual     : {branch}")
    print(f"Rama desarrollo : {project_value('default_branch', 'develop')}")
    print(f"Rama producción : {project_value('production_branch', 'main')}")
    print(f"Estado          : {status_label()}")
    print(f"GitHub          : {sync_label(branch)}")
    print(f"Publicación     : {publication_label()}")
    print(f"Archivos Git    : {count_files()}")
    print(f"Commits rama    : {count_commits()}")
    print(f"Último commit   : {commit_hash}  {subject}")
    print(f"Fecha           : {date_}")
    print(f"GitHub URL      : {project_value('github_url')}")
    print(f"Preview URL     : {project_value('preview_url') or '(no configurada)'}")
    print(f"Producción      : {project_value('site_url')}")


def show_diff() -> None:
    print("\nCAMBIOS NO PREPARADOS:")
    diff = run_git(["diff"], capture=True).stdout.strip()
    print(diff if diff else "(ninguno)")

    print("\nCAMBIOS PREPARADOS PARA COMMIT:")
    cached = run_git(["diff", "--cached"], capture=True).stdout.strip()
    print(cached if cached else "(ninguno)")


def show_graph() -> None:
    print()
    graph = run_git(
        ["log", "--graph", "--decorate", "--oneline", "--all", "-35"],
        capture=True,
    ).stdout.strip()
    print(graph if graph else "(sin historial)")


def branch_summary() -> None:
    develop = project_value("default_branch", "develop")
    main = project_value("production_branch", "main")
    d_hash, d_subject, d_date = last_commit(develop)
    m_hash, m_subject, m_date = last_commit(main)
    relation = develop_vs_main()

    print("\n" + "=" * 72)
    print("RESUMEN DE RAMAS")
    print("=" * 72)
    print(f"DEVELOP  {d_hash}  {d_subject}")
    print(f"         {d_date}")
    print()
    print(f"MAIN     {m_hash}  {m_subject}")
    print(f"         {m_date}")
    print("-" * 72)

    if relation is None:
        print("No fue posible comparar las ramas.")
        return

    main_only, develop_only = relation
    print(f"Commits solo en MAIN    : {main_only}")
    print(f"Commits solo en DEVELOP : {develop_only}")
    print(f"Estado                  : {publication_label()}")


def list_and_switch_branch() -> None:
    ensure_clean()
    branches = run_git(
        ["for-each-ref", "--format=%(refname:short)", "refs/heads/"],
        capture=True,
    ).stdout.splitlines()

    print("\nRAMAS LOCALES:")
    current = current_branch()
    for idx, branch in enumerate(branches, 1):
        marker = "*" if branch == current else " "
        print(f"{idx:2d} {marker} {branch}")

    choice = input("\nNúmero de rama (ENTER cancela): ").strip()
    if not choice:
        print("Operación cancelada.")
        return

    try:
        branch = branches[int(choice) - 1]
    except (ValueError, IndexError):
        raise AppError("Selección inválida.")

    if branch == current:
        print(f"Ya está en '{branch}'.")
        return

    switch_branch(branch)
    print(f"\n✓ Rama actual: {branch}")


def push_changes() -> None:
    branch = current_branch()
    default = project_value("default_branch", "develop")

    if branch != default:
        confirm = input(
            f"\nEstá en '{branch}', no en '{default}'. ¿Continuar? [s/N]: "
        ).strip().lower()
        if confirm not in {"s", "si", "sí", "y", "yes"}:
            print("Operación cancelada.")
            return

    changes = short_status()
    if not changes:
        print("\nNo hay cambios para publicar.")
        return

    print("\nARCHIVOS MODIFICADOS:")
    print(changes)
    print("\nRevise la opción 'Ver diferencias' antes de continuar.")

    message = input("\nMensaje del commit: ").strip()
    if not message:
        raise AppError("El mensaje del commit no puede estar vacío.")

    run_git(["add", "-A"])
    run_git(["commit", "-m", message])
    run_git(["push", project_value("remote", "origin"), branch])

    log(f"{project_value('name')} | PUSH OK | branch={branch} | commit={message}")
    print("\n✓ Commit y push completados.")


def publish_to_main() -> None:
    ensure_clean()

    develop = project_value("default_branch", "develop")
    main = project_value("production_branch", "main")
    relation = develop_vs_main()

    if relation is not None:
        main_only, develop_only = relation
        if main_only > 0:
            raise AppError(
                "MAIN contiene commits que DEVELOP no tiene.\n"
                "Las ramas están divergentes. Revise antes de publicar."
            )
        if develop_only == 0:
            print("\nMAIN ya está actualizado. No hay nada que publicar.")
            return

    original_branch = current_branch()
    d_hash, d_subject, d_date = last_commit(develop)

    print("\n" + "=" * 72)
    print("PUBLICAR EN PRODUCCIÓN")
    print("=" * 72)
    print(f"Proyecto     : {project_value('name')}")
    print(f"Origen       : {develop}")
    print(f"Destino      : {main}")
    print(f"Commit       : {d_hash}  {d_subject}")
    print(f"Fecha        : {d_date}")
    print(f"Sitio        : {project_value('site_url')}")
    print("-" * 72)
    print("Esta acción actualizará MAIN y activará el despliegue de Cloudflare.")
    confirm = input("Escriba exactamente PUBLICAR para continuar: ").strip()

    if confirm != "PUBLICAR":
        print("Operación cancelada.")
        return

    try:
        switch_branch(develop)
        run_git(["pull", "--ff-only", project_value("remote", "origin"), develop])

        switch_branch(main)
        run_git(["pull", "--ff-only", project_value("remote", "origin"), main])

        merge = run_git(["merge", "--ff-only", develop], capture=True, check=False)
        if merge.returncode != 0:
            detail = (merge.stderr or merge.stdout).strip()
            raise AppError(
                "No fue posible hacer fast-forward.\n"
                "Producción NO fue modificada.\n\n"
                f"{detail}"
            )

        run_git(["push", project_value("remote", "origin"), main])
        log(f"{project_value('name')} | PUBLISH OK | {develop}->{main}")
        print("\n✓ Producción publicada correctamente.")
    finally:
        if current_branch() != original_branch:
            run_git(["switch", original_branch], check=False)


def open_folder() -> None:
    if os.name == "nt":
        os.startfile(str(repo_path()))  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", str(repo_path())], check=False)


def open_code() -> None:
    code = shutil.which("code")
    if not code:
        raise AppError("VS Code no está disponible mediante el comando 'code'.")
    subprocess.Popen([code, str(repo_path())], cwd=repo_path())


def open_url(key: str) -> None:
    url = str(project_value(key, "")).strip()
    if not url:
        raise AppError(
            f"No existe una URL configurada para '{key}'.\n"
            "Edite config.json y complete ese valor."
        )
    webbrowser.open(url)


def print_menu() -> None:
    print("REPOSITORIO")
    print(" 1 - Actualizar desde GitHub (Pull)")
    print(" 2 - Ver estado")
    print(" 3 - Ver diferencias")
    print(" 4 - Ver historial gráfico")
    print(" 5 - Ver resumen de ramas")
    print(" 6 - Cambiar de rama")
    print(" 7 - Información del proyecto")
    print()
    print("PUBLICAR")
    print(" 8 - Commit + Push")
    print(" 9 - Publicar develop → main")
    print()
    print("PORTAL")
    print("10 - Abrir GitHub")
    print("11 - Abrir Cloudflare")
    print("12 - Abrir Preview")
    print("13 - Abrir menezes.pro")
    print()
    print("LOCAL")
    print("14 - Abrir carpeta")
    print("15 - Abrir VS Code")
    print()
    print(" 0 - Salir")


def menu() -> None:
    actions = {
        "1": pull,
        "2": show_status,
        "3": show_diff,
        "4": show_graph,
        "5": branch_summary,
        "6": list_and_switch_branch,
        "7": show_project_info,
        "8": push_changes,
        "9": publish_to_main,
        "10": lambda: open_url("github_url"),
        "11": lambda: open_url("cloudflare_url"),
        "12": lambda: open_url("preview_url"),
        "13": lambda: open_url("site_url"),
        "14": open_folder,
        "15": open_code,
    }

    while True:
        clear()
        validate_environment()
        print_header()
        print_menu()

        option = input("\nSeleccione una opción: ").strip()
        if option == "0":
            print("\nHasta luego.")
            return

        action = actions.get(option)
        if not action:
            print("\nOpción inválida.")
            pause()
            continue

        try:
            action()
        except AppError as exc:
            log(f"{project_value('name')} | ERROR | {exc}")
            print(f"\nERROR:\n{exc}")
        except KeyboardInterrupt:
            print("\nOperación cancelada.")
        except Exception as exc:
            log(f"{project_value('name')} | ERROR INESPERADO | {type(exc).__name__}: {exc}")
            print(f"\nERROR INESPERADO: {exc}")

        pause()


def main() -> int:
    try:
        select_project()
        validate_environment()
        menu()
        return 0
    except AppError as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
