from contextlib import closing
from importlib import import_module
from socket import socket
from types import ModuleType
from typing import Any, List, Type


def find_builtin_server_type(type_name: str) -> Type[Any]:
    """Find first installed server implementation"""
    builtin_module_names = ["sanic", "flask", "tornado"]

    installed_builtin_modules: List[ModuleType] = []
    for module_name in builtin_module_names:
        try:
            installed_builtin_modules.append(
                import_module(f"idom.server.{module_name}")
            )
        except ImportError:  # coverage: skip
            pass

    if not installed_builtin_modules:  # coverage: skip
        raise RuntimeError(
            f"Found none of the following builtin server implementations {builtin_module_names}"
        )

    for builtin_module in installed_builtin_modules:
        try:
            return getattr(builtin_module, type_name)  # type: ignore
        except AttributeError:  # coverage: skip
            pass
    else:  # coverage: skip
        installed_names = [m.__name__ for m in installed_builtin_modules]
        raise ImportError(
            f"No server type {type_name!r} found in installed implementations {installed_names}"
        )


def find_available_port(host: str, port_min: int = 8000, port_max: int = 9000) -> int:
    """Get a port that's available for the given host and port range"""
    for port in range(port_min, port_max):
        with closing(socket()) as sock:
            try:
                sock.bind((host, port))
            except OSError:
                pass
            else:
                return port
    raise RuntimeError(
        f"Host {host!r} has no available port in range {port_max}-{port_max}"
    )
