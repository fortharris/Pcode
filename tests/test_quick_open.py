from Extensions.QuickOpen import fuzzy_matches, index_project_files


def test_fuzzy_matches():
    assert fuzzy_matches("", "anything")
    assert fuzzy_matches("ab", "alpha/beta.py")
    assert not fuzzy_matches("xyz", "alpha/beta.py")


def test_index_project_files(tmp_path):
    (tmp_path / "a.py").write_text("x\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.py").write_text("y\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("z\n", encoding="utf-8")
    files = index_project_files(str(tmp_path))
    rels = {rel for rel, _ in files}
    assert "a.py" in rels
    assert "sub/b.py" in rels or "sub\\b.py" in rels
    assert not any(".git" in rel for rel in rels)
