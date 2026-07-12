import ast
from pathlib import Path

CONTRACTS_ROOT = Path(__file__).resolve().parents[3] / "app" / "contracts"
FORBIDDEN_IMPORTS = ("alembic", "fastapi", "sqlalchemy", "app.api", "app.db")


def test_contracts_do_not_import_framework_or_persistence_modules() -> None:
    violations: list[str] = []
    for path in CONTRACTS_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                modules.append(node.module)
            for module in modules:
                if module.startswith(FORBIDDEN_IMPORTS):
                    violations.append(f"{path.relative_to(CONTRACTS_ROOT)} imports {module}")
    assert violations == []
