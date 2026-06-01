from pathlib import Path

import pytest
import yaml

from flashalpha_examples_tools.verify_frontmatter import (
    FrontmatterMismatch, extract_frontmatter, verify_essay_frontmatter,
)


FIX = Path(__file__).parent / "fixtures" / "sample-essay"


def test_extract_frontmatter_from_readme():
    fm = extract_frontmatter(FIX / "README.md")
    assert fm["slug"] == "sample"
    assert fm["theme"] == "dealer-positioning"


def test_verify_passes_when_in_sync():
    verify_essay_frontmatter(FIX)  # no exception


def test_verify_fails_on_drift(tmp_path: Path):
    # Copy fixtures, mutate meta.yaml, expect FrontmatterMismatch
    import shutil
    drifted = tmp_path / "drifted"
    shutil.copytree(FIX, drifted)
    meta = yaml.safe_load((drifted / "meta.yaml").read_text())
    meta["title"] = "Different title"
    (drifted / "meta.yaml").write_text(yaml.safe_dump(meta))

    with pytest.raises(FrontmatterMismatch, match="title"):
        verify_essay_frontmatter(drifted)


def test_verify_fails_on_invalid_schema(tmp_path: Path):
    import shutil
    bad = tmp_path / "bad"
    shutil.copytree(FIX, bad)
    text = (bad / "README.md").read_text().replace("difficulty: beginner", "difficulty: expert")
    (bad / "README.md").write_text(text)
    # Also drift meta.yaml to match — otherwise we'd catch a FrontmatterMismatch first
    meta = yaml.safe_load((bad / "meta.yaml").read_text())
    meta["difficulty"] = "expert"
    (bad / "meta.yaml").write_text(yaml.safe_dump(meta))

    with pytest.raises(Exception):  # ValidationError from _schema, propagated
        verify_essay_frontmatter(bad)
