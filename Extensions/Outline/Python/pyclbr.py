"""
AST-based outline for the Python outline explorer.

Keeps the same Class / Function / GlobalVariable shapes expected by Outline.py.
"""

from __future__ import annotations

import ast


class Class:
    """Class to represent a Python class."""

    def __init__(self, name, super, lineno):
        self.name = name
        if super is None:
            super = []
        self.super = super
        self.methods = {}
        self.lineno = lineno
        self.objectType = "Class"

    def _addmethod(self, name, lineno):
        self.methods[name] = lineno


class Function:
    """Class to represent a top-level Python function."""

    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno
        self.objectType = "Function"


class GlobalVariable:
    """Class to represent a top-level Python global variable."""

    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno
        self.objectType = "GlobalVariable"


def _base_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        try:
            return ast.unparse(node)
        except Exception:
            return node.attr
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _assign_names(node):
    names = []
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                names.append(target.id)
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            names.append(node.target.id)
    return names


def readmodule(source):
    res = {}
    for key, value in _readmodule(source).items():
        if isinstance(value, Class):
            res[key] = value
    return res


def _readmodule(source):
    outlineDict = {}
    try:
        tree = ast.parse(source or "")
    except SyntaxError:
        return outlineDict

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = []
            for base in node.bases:
                name = _base_name(base)
                if name:
                    bases.append(name)
            cur_class = Class(node.name, bases, node.lineno)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    cur_class._addmethod(item.name, item.lineno)
            outlineDict[node.name] = cur_class
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            outlineDict[node.name] = Function(node.name, node.lineno)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            for name in _assign_names(node):
                outlineDict[name] = GlobalVariable(name, node.lineno)

    return outlineDict
