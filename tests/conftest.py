"""
Pytest configuration and shared fixtures for KeyClave tests.

Provides fixtures for temporary vaults, mock profiles, test data, and Qt application setup.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory that is cleaned up after the test."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_vault_dir(temp_dir: Path) -> Path:
    """Provide a temporary directory for vault storage."""
    vault_dir = temp_dir / "vaults"
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir


@pytest.fixture
def sample_passphrase() -> str:
    """Provide a sample passphrase for testing."""
    return "test-passphrase-secure-123"


@pytest.fixture
def sample_secret_data() -> dict:
    """Provide sample secret data for testing."""
    return {
        "key_name": "GITHUB_TOKEN",
        "key_value": "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
        "provider": "github",
        "project_path": "/test/project",
        "notes": "Test GitHub token",
    }


# Qt-specific fixtures will be added here when implementing UI tests
# Example:
# @pytest.fixture
# def qapp(qtbot):
#     """Provide QApplication instance for Qt tests."""
#     from PySide6.QtWidgets import QApplication
#     return QApplication.instance() or QApplication([])
