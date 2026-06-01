from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def essays_dir(repo_root: Path) -> Path:
    return repo_root / "essays"
