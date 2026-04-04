from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend" / "app"


def _module_name(path: Path) -> str:
    return ".".join(path.relative_to(PROJECT_ROOT / "backend").with_suffix("").parts)


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    module_name = _module_name(path)
    package_parts = module_name.split(".")[:-1]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if node.level == 0:
                    imports.add(node.module)
                else:
                    prefix = package_parts[:- (node.level - 1)] if node.level > 1 else package_parts
                    resolved = ".".join(prefix + node.module.split("."))
                    imports.add(resolved)
            elif node.level > 0:
                prefix = package_parts[:- (node.level - 1)] if node.level > 1 else package_parts
                imports.add(".".join(prefix))
    return imports


def test_service_modules_do_not_import_route_modules() -> None:
    offenders: list[str] = []
    for path in (BACKEND_ROOT / "services").glob("*.py"):
        imports = _imported_modules(path)
        bad = sorted(
            module
            for module in imports
            if module.startswith("app.api.") or module.endswith(".routes") or ".routes." in module
        )
        if bad:
            offenders.append(f"{path.name}: {', '.join(bad)}")

    assert not offenders, "Service layer must not depend on route modules:\n" + "\n".join(offenders)


def test_route_modules_do_not_import_other_route_modules() -> None:
    offenders: list[str] = []
    route_paths = list((BACKEND_ROOT / "api").glob("*routes.py")) + [
        BACKEND_ROOT / "calendar" / "routes.py",
        BACKEND_ROOT / "festivals" / "routes.py",
    ]
    for path in route_paths:
        imports = _imported_modules(path)
        own_module = _module_name(path)
        compatibility_wrapper = own_module in {"app.api.calendar_routes", "app.api.festival_routes"}
        bad = sorted(
            module
            for module in imports
            if (module.startswith("app.api.") and module.endswith("_routes"))
            or module in {"app.calendar.routes", "app.festivals.routes"}
        )
        bad = [module for module in bad if module != own_module]
        if "app.services" in imports:
            bad.append("app.services")
        if compatibility_wrapper:
            bad = [module for module in bad if module not in {"app.calendar.routes", "app.festivals.routes"}]
        if bad:
            offenders.append(f"{path.relative_to(PROJECT_ROOT)}: {', '.join(sorted(set(bad)))}")

    assert not offenders, "Route modules should depend on use cases/services, not other routes:\n" + "\n".join(offenders)


def test_infrastructure_layers_do_not_import_fastapi() -> None:
    offenders: list[str] = []
    for folder in ("storage", "infrastructure"):
        for path in (BACKEND_ROOT / folder).glob("*.py"):
            imports = _imported_modules(path)
            bad = sorted(module for module in imports if module == "fastapi" or module.startswith("fastapi."))
            if bad:
                offenders.append(f"{path.name}: {', '.join(bad)}")

    assert not offenders, "Infrastructure/storage modules must stay framework-agnostic:\n" + "\n".join(offenders)
