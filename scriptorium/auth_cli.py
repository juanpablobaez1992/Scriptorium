"""
auth_cli.py
CLI para generar hash y rotar credenciales locales de autenticacion.
Uso: python -m scriptorium.auth_cli <comando>
"""

from __future__ import annotations

import argparse
import getpass
from pathlib import Path

from dotenv import dotenv_values
from werkzeug.security import generate_password_hash


def _read_password_from_prompt() -> str:
    password = getpass.getpass("Nueva clave: ")
    confirm = getpass.getpass("Confirmar clave: ")
    if not password:
        raise ValueError("La clave no puede ser vacia.")
    if password != confirm:
        raise ValueError("Las claves no coinciden.")
    return password


def _upsert_env_var(lines: list[str], key: str, value: str) -> list[str]:
    replaced = False
    output: list[str] = []
    prefix = f"{key}="
    for line in lines:
        normalized = line.lstrip("\ufeff")
        if normalized.startswith(prefix):
            if not replaced:
                output.append(f"{prefix}{value}")
                replaced = True
            continue
        output.append(line)
    if not replaced:
        output.append(f"{prefix}{value}")
    return output


def _remove_env_var(lines: list[str], key: str) -> list[str]:
    prefix = f"{key}="
    return [line for line in lines if not line.lstrip("\ufeff").startswith(prefix)]


def _load_env_lines(env_path: Path) -> list[str]:
    if not env_path.exists():
        return []
    return env_path.read_text(encoding="utf-8").splitlines()


def _save_env_lines(env_path: Path, lines: list[str]) -> None:
    body = "\n".join(lines).rstrip() + "\n"
    env_path.write_text(body, encoding="utf-8")


def command_hash(args: argparse.Namespace) -> int:
    password = args.password or _read_password_from_prompt()
    print(generate_password_hash(password))
    return 0


def command_rotate(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file).resolve()
    env_data = dotenv_values(env_path)
    username = args.username or str(env_data.get("AUTH_USERNAME") or "admin")
    password = args.password or _read_password_from_prompt()
    password_hash = generate_password_hash(password)

    lines = _load_env_lines(env_path)
    lines = _upsert_env_var(lines, "AUTH_USERNAME", username)
    lines = _upsert_env_var(lines, "AUTH_PASSWORD_HASH", password_hash)
    lines = _remove_env_var(lines, "AUTH_PASSWORD")
    _save_env_lines(env_path, lines)

    print(f"Credenciales actualizadas en: {env_path}")
    print("Variables actualizadas: AUTH_USERNAME, AUTH_PASSWORD_HASH")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m scriptorium.auth_cli",
        description="Gestion de credenciales de autenticacion local.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    hash_parser = subparsers.add_parser("hash", help="Genera hash desde una clave.")
    hash_parser.add_argument("--password", help="Clave en texto plano (evitar en historial).")
    hash_parser.set_defaults(handler=command_hash)

    rotate_parser = subparsers.add_parser("rotate", help="Rota credenciales y actualiza .env.")
    rotate_parser.add_argument("--env-file", default=".env", help="Ruta del archivo .env.")
    rotate_parser.add_argument("--username", help="Nuevo usuario. Si falta, conserva AUTH_USERNAME.")
    rotate_parser.add_argument("--password", help="Nueva clave en texto plano (evitar en historial).")
    rotate_parser.set_defaults(handler=command_rotate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
