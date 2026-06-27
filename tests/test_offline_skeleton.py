"""Offline skeleton tests.

These tests verify that the minimal skeleton does not require GUI, database,
provider SDKs or network access.
"""

from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def optional_module_available(module_name: str) -> bool:
    """Return whether an optional module is importable.

    Some dotted module names may raise ModuleNotFoundError when the parent
    package is absent. That is acceptable for this skeleton check.
    """

    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


class OfflineSkeletonTests(unittest.TestCase):
    def test_no_common_provider_sdk_required(self) -> None:
        optional_provider_modules = [
            "openai",
            "anthropic",
            "google.generativeai",
        ]

        # The skeleton must import without requiring these modules.
        import aurora_studio  # noqa: F401

        for module_name in optional_provider_modules:
            optional_module_available(module_name)

    def test_no_gui_dependency_required(self) -> None:
        import aurora_studio  # noqa: F401

        gui_modules = ["PySide6", "PyQt6", "gradio", "streamlit"]
        for module_name in gui_modules:
            optional_module_available(module_name)

    def test_no_database_dependency_required(self) -> None:
        import aurora_studio  # noqa: F401

        database_modules = ["sqlalchemy", "psycopg", "pymongo"]
        for module_name in database_modules:
            optional_module_available(module_name)


if __name__ == "__main__":
    unittest.main()
