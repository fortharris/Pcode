from Extensions.Outline.Python import pyclbr


SOURCE = '''\
X = 1
Y: int = 2

class Base:
    def method(self):
        pass

async def agen():
    pass

def top(a, b):
    return a + b

class Child(Base):
    def __init__(self):
        self.x = 1

    async def work(self):
        return self.x
'''


def test_outline_reads_classes_functions_and_globals():
    outline = pyclbr._readmodule(SOURCE)
    assert "Base" in outline
    assert outline["Base"].objectType == "Class"
    assert "method" in outline["Base"].methods
    assert "Child" in outline
    assert "__init__" in outline["Child"].methods
    assert "work" in outline["Child"].methods
    assert outline["top"].objectType == "Function"
    assert outline["agen"].objectType == "Function"
    assert outline["X"].objectType == "GlobalVariable"
    assert outline["Y"].objectType == "GlobalVariable"


def test_outline_syntax_error_returns_empty():
    assert pyclbr._readmodule("def (") == {}


def test_external_launcher_path_validation():
    from Extensions.ExternalLauncher import _is_safe_launcher_path, _split_params
    ok, msg = _is_safe_launcher_path("relative.exe")
    assert not ok
    assert _split_params('--flag "a b"') == ["--flag", "a b"]
