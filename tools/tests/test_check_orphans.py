from pathlib import Path
import shutil

import pytest

from flashalpha_examples_tools.check_orphans import (
    OrphanError, check_essay_shape, find_orphans,
)


FIX = Path(__file__).parent / "fixtures" / "sample-essay"


@pytest.fixture
def essay_dir(tmp_path: Path) -> Path:
    """Copy the sample essay fixture + scaffold required language dirs."""
    d = tmp_path / "01-sample"
    shutil.copytree(FIX, d)
    # Scaffold the required dirs:
    for sub in ("python", "csharp", "results"):
        (d / sub).mkdir()
    (d / "python" / "main.py").write_text("# stub\n")
    (d / "python" / "config.json").write_text("{}\n")
    (d / "python" / "lean.json").write_text("{}\n")
    (d / "python" / "golden.json").write_text("{}\n")
    (d / "python" / "requirements.txt").write_text("flashalpha-quantconnect==0.1.1\n")
    (d / "csharp" / "Main.cs").write_text("// stub\n")
    (d / "csharp" / "config.json").write_text("{}\n")
    (d / "csharp" / "lean.json").write_text("{}\n")
    (d / "csharp" / "golden.json").write_text("{}\n")
    (d / "csharp" / "Sample.csproj").write_text("<Project/>\n")
    (d / "references.md").write_text("- Sample reference\n")
    return d


def test_complete_essay_passes(essay_dir: Path):
    check_essay_shape(essay_dir)  # no exception


def test_missing_python_main_fails(essay_dir: Path):
    (essay_dir / "python" / "main.py").unlink()
    with pytest.raises(OrphanError, match="python/main.py"):
        check_essay_shape(essay_dir)


def test_missing_csharp_csproj_fails(essay_dir: Path):
    (essay_dir / "csharp" / "Sample.csproj").unlink()
    with pytest.raises(OrphanError, match="\\.csproj"):
        check_essay_shape(essay_dir)


def test_missing_references_fails(essay_dir: Path):
    (essay_dir / "references.md").unlink()
    with pytest.raises(OrphanError, match="references.md"):
        check_essay_shape(essay_dir)


def test_find_orphans_walks_themes(tmp_path: Path, essay_dir: Path):
    # Build a tiny mock repo structure
    repo = tmp_path / "repo"
    essays = repo / "essays" / "a-dealer-positioning"
    essays.mkdir(parents=True)
    shutil.copytree(essay_dir, essays / "01-sample")

    issues = find_orphans(repo)
    assert issues == []


def test_find_orphans_finds_broken_essay(tmp_path: Path, essay_dir: Path):
    repo = tmp_path / "repo"
    essays = repo / "essays" / "a-dealer-positioning"
    essays.mkdir(parents=True)
    shutil.copytree(essay_dir, essays / "01-sample")
    (essays / "01-sample" / "python" / "main.py").unlink()

    issues = find_orphans(repo)
    assert len(issues) == 1
    assert "main.py" in issues[0]
