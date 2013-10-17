"""
Class Outline based on the python 3 pyclbr
"""

import re
import io
import tokenize
from token import NAME, DEDENT, OP

_modules = {}
# cache of modules we've seen

spacesFirstWordRe = re.compile(r"^(\s*)(\w*)")
getSpacesFirstWord = lambda s, c=spacesFirstWordRe: c.match(s).groups()

# each Python class is represented by an instance of this class
class Class:

    '''Class to represent a Python class.'''

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

    '''Class to represent a top-level Python function'''

    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno

        self.objectType = "Function"


class GlobalVariable:

    '''Class to represent a top-level Python global variable'''

    def __init__(self, name, lineno):
        self.name = name
        self.lineno = lineno

        self.objectType = "GlobalVariable"


def readmodule(source):

    res = {}
    for key, value in _readmodule(source).items():
        if isinstance(value, Class):
            res[key] = value
    return res


def _readmodule(source):
    outlineDict = {}

    f = io.StringIO(source)

    stack = []  # stack of (class, indent) pairs

    g = tokenize.generate_tokens(f.readline)
    try:
        for tokentype, token, start, _end, _line in g:
            if tokentype == DEDENT:
                lineno, thisindent = start
                # close nested classes and defs
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]
            elif token == 'def':
                lineno, thisindent = start
                # close previous nested classes and defs
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]
                tokentype, meth_name, start = next(g)[0:3]
                if tokentype != NAME:
                    continue  # Syntax error
                if stack:
                    cur_class = stack[-1][0]
                    if isinstance(cur_class, Class):
                        # it's a method
                        cur_class._addmethod(meth_name, lineno)
                    # else it's a nested def
                else:
                    # it's a function
                    outlineDict[meth_name] = Function(meth_name, lineno)
                stack.append((None, thisindent))  # Marker for nested fns
            elif token == 'class':
                lineno, thisindent = start
                # close previous nested classes and defs
                while stack and stack[-1][1] >= thisindent:
                    del stack[-1]
                tokentype, class_name, start = next(g)[0:3]
                if tokentype != NAME:
                    continue  # Syntax error
                # parse what follows the class name
                tokentype, token, start = next(g)[0:3]
                inherit = None
                if token == '(':
                    names = []  # List of superclasses
                    # there's a list of superclasses
                    level = 1
                    super = []  # Tokens making up current superclass
                    while True:
                        tokentype, token, start = next(g)[0:3]
                        if token in (')', ',') and level == 1:
                            n = "".join(super)
                            if n in outlineDict:
                                # we know this super class
                                n = outlineDict[n]
                            else:
                                c = n.split('.')
                                if len(c) > 1:
                                    # super class is of the form
                                    # module.class: look in module for
                                    # class
                                    m = c[-2]
                                    c = c[-1]
                                    if m in _modules:
                                        d = _modules[m]
                                        if c in d:
                                            n = d[c]
                            names.append(n)
                            super = []
                        if token == '(':
                            level += 1
                        elif token == ')':
                            level -= 1
                            if level == 0:
                                break
                        elif token == ',' and level == 1:
                            pass
                        # only use NAME and OP (== dot) tokens for type name
                        elif tokentype in (NAME, OP) and level == 1:
                            super.append(token)
                        # expressions in the base list are not supported
                    inherit = names
                cur_class = Class(class_name, inherit,
                                  lineno)
                if not stack:
                    outlineDict[class_name] = cur_class
                stack.append((cur_class, thisindent))
            elif token == '=':
                # get global variables
                spaces, firstword = getSpacesFirstWord(_line)
                if (len(spaces) == 0) and (_line.lstrip(spaces + firstword).lstrip().startswith('=')):
                    # it's a global variable
                    lineno, thisindent = start
                    outlineDict[firstword] = GlobalVariable(firstword, lineno)
    except:
        pass

    f.close()
    return outlineDict
