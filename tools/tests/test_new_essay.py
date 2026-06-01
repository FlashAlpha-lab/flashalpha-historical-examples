from pathlib import Path

import pytest

from flashalpha_examples_tools.new_essay import scaffold_essay
from flashalpha_examples_tools.check_orphans import check_essay_shape


def test_scaffold_creates_complete_essay(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "essays" / "a-dealer-positioning").mkdir(parents=True)
    essay = scaffold_essay(
        repo, theme_slug="dealer-positioning",
        slug="gamma-flip", title="Gamma flip strike trading",
        number=3,
    )
    # Required shape passes
    check_essay_shape(essay)
    # README has frontmatter
    text = (essay / "README.md").read_text()
    assert text.startswith("---")
    assert "gamma-flip" in text


def test_scaffold_rejects_existing_dir(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "essays" / "a-dealer-positioning" / "03-gamma-flip").mkdir(parents=True)
    with pytest.raises(FileExistsError):
        scaffold_essay(repo, theme_slug="dealer-positioning",
                       slug="gamma-flip", title="X", number=3)
