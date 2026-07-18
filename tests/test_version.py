from Extensions.version import VERSION, parse_version


def test_version_matches_pyproject():
    text = open("pyproject.toml", encoding="utf-8").read()
    assert f'version = "{VERSION}"' in text


def test_parse_version_orders():
    assert parse_version("0.2.0") > parse_version("0.1.5")
    assert parse_version("v0.2.0") == parse_version("0.2.0")
    assert parse_version("1.0") > parse_version("0.9.9")


def test_about_uses_version_constant():
    import Extensions.About as about_mod
    assert about_mod.VERSION == VERSION
