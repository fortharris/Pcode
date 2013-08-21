# -*- coding: utf-8 -*-

# Copyright (c) 2005 - 2012 Detlev Offenbach <detlev@die-offenbachs.de>
#
"""
Parse a Python file and retrieve classes, functions/methods and attributes.

Parse enough of a Python file to recognize class and method definitions and
to find out the superclasses of a class as well as its attributes.

This is module is based on pyclbr found in the Python 2.2.2 distribution.
"""


import re

from Extensions.Outline.Python import BaseClassBrowser as BaseClassBrowser
from functools import reduce

TABWIDTH = 4

_getnext = re.compile(r"""
    (?P<String>
       \""" [^"\\]* (?:
                        (?: \\. | "(?!"") )
                        [^"\\]*
                    )*
       \"""

    |   ''' [^'\\]* (?:
                        (?: \\. | '(?!'') )
                        [^'\\]*
                    )*
        '''

    |   " [^"\\\n]* (?: \\. [^"\\\n]*)* "

    |   ' [^'\\\n]* (?: \\. [^'\\\n]*)* '
    )

|   (?P<Publics>
        ^
        [ \t]* __all__ [ \t]* = [ \t]* \[
        (?P<Identifiers> [^\]]*? )
        \]
    )

|   (?P<MethodModifier>
        ^
        (?P<MethodModifierIndent> [ \t]* )
        (?P<MethodModifierType> @classmethod | @staticmethod )
    )

|   (?P<Method>
        ^
        (?P<MethodIndent> [ \t]* )
        def [ \t]+
        (?P<MethodName> \w+ )
        (?: [ \t]* \[ (?: plain | html ) \] )?
        [ \t]* \(
        (?P<MethodSignature> (?: [^)] | \)[ \t]*,? )*? )
        \) [ \t]* :
    )

|   (?P<Class>
        ^
        (?P<ClassIndent> [ \t]* )
        class [ \t]+
        (?P<ClassName> \w+ )
        [ \t]*
        (?P<ClassSupers> \( [^)]* \) )?
        [ \t]* :
    )

|   (?P<Attribute>
        ^
        (?P<AttributeIndent> [ \t]* )
        self [ \t]* \. [ \t]*
        (?P<AttributeName> \w+ )
        [ \t]* =
    )

|   (?P<Variable>
        ^
        (?P<VariableIndent> [ \t]* )
        (?P<VariableName> \w+ )
        [ \t]* =
    )

|   (?P<ConditionalDefine>
        ^
        (?P<ConditionalDefineIndent> [ \t]* )
        (?: (?: if | elif ) [ \t]+ [^:]* | else [ \t]* ) : (?= \s* def)
    )

|   (?P<CodingLine>
        ^ \# \s* [*_-]* \s* coding[:=] \s* (?P<Coding> [-\w_.]+ ) \s* [*_-]* $
    )
""", re.VERBOSE | re.DOTALL | re.MULTILINE).search

_commentsub = re.compile(r"""#[^\n]*\n|#[^\n]*$""").sub

_modules = {}                           # cache of modules we've seen


class Class(BaseClassBrowser.Class):
    """
    Class to represent a Python class.
    """
    def __init__(self, module, name, super, lineno):
        """
        Constructor

        @param module name of the module containing this class
        @param name name of this class
        @param super list of class names this class is inherited from
        @param file filename containing this class
        @param lineno linenumber of the class definition
        """
        BaseClassBrowser.Class.__init__(self, module, name, super, lineno)


class Function(BaseClassBrowser.Function):
    """
    Class to represent a Python function.
    """
    def __init__(self, module, name, lineno, signature='', separator=',',
                 modifierType=BaseClassBrowser.Function.General):
        """
        Constructor

        @param module name of the module containing this function
        @param name name of this function
        @param file filename containing this class
        @param lineno linenumber of the class definition
        @param signature parameterlist of the method
        @param separator string separating the parameters
        @param modifierType type of the function
        """
        BaseClassBrowser.Function.__init__(self, module, name, lineno,
                                           signature, separator, modifierType)


class Attribute(BaseClassBrowser.Attribute):
    """
    Class to represent a class attribute.
    """
    def __init__(self, module, name, lineno):
        """
        Constructor

        @param module name of the module containing this class
        @param name name of this class
        @param file filename containing this attribute
        @param lineno linenumber of the class definition
        """
        BaseClassBrowser.Attribute.__init__(self, module, name, lineno)


class Publics(object):
    """
    Class to represent the list of public identifiers.
    """
    def __init__(self, module, lineno, idents):
        """
        Constructor

        @param module name of the module containing this function
        @param file filename containing this class
        @param lineno linenumber of the class definition
        @param idents list of public identifiers
        """
        self.module = module
        self.name = '__all__'
        self.lineno = lineno
        self.identifiers = [e.replace('"', '').replace("'", "").strip()
                            for e in idents.split(',')]


def readmodule_ex(src):
    '''
    Read a module file and return a dictionary of classes.

    Search for MODULE in PATH and sys.path, read and parse the
    module and return a dictionary with one entry for each class
    found in the module.

    @param module name of the module file (string)
    @param path path the module should be searched in (list of strings)
    @param inpackage flag indicating a module inside a package is scanned
    @return the resulting dictionary
    '''
    global _modules

    dict = {}
    dict_counts = {}

    module = "pCode"
    _modules[module] = dict
    classstack = []  # stack of (class, indent) pairs
    conditionalsstack = []  # stack of indents of conditional defines
    deltastack = []
    deltaindent = 0
    deltaindentcalculated = 0

    lineno, last_lineno_pos = 1, 0
    i = 0
    modifierType = BaseClassBrowser.Function.General
    modifierIndent = -1
    while True:
        m = _getnext(src, i)
        if not m:
            break
        start, i = m.span()

        if m.start("MethodModifier") >= 0:
            modifierIndent = _indent(m.group("MethodModifierIndent"))
            modifierType = m.group("MethodModifierType")

        elif m.start("Method") >= 0:
            # found a method definition or function
            thisindent = _indent(m.group("MethodIndent"))
            meth_name = m.group("MethodName")
            meth_sig = m.group("MethodSignature")
            meth_sig = meth_sig.replace('\\\n', '')
            meth_sig = _commentsub('', meth_sig)
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            if modifierType and modifierIndent == thisindent:
                if modifierType == "@staticmethod":
                    modifier = BaseClassBrowser.Function.Static
                elif modifierType == "@classmethod":
                    modifier = BaseClassBrowser.Function.Class
                else:
                    modifier = BaseClassBrowser.Function.General
            else:
                modifier = BaseClassBrowser.Function.General
            # modify indentation level for conditional defines
            if conditionalsstack:
                if thisindent > conditionalsstack[-1]:
                    if not deltaindentcalculated:
                        deltastack.append(thisindent - conditionalsstack[-1])
                        deltaindent = reduce(lambda x, y:  x + y, deltastack)
                        deltaindentcalculated = 1
                    thisindent -= deltaindent
                else:
                    while conditionalsstack and \
                            conditionalsstack[-1] >= thisindent:
                        del conditionalsstack[-1]
                        if deltastack:
                            del deltastack[-1]
                    deltaindentcalculated = 0
            # close all classes indented at least as much
            while classstack and \
                    classstack[-1][1] >= thisindent:
                del classstack[-1]
            if classstack:
                # it's a class method
                cur_class = classstack[-1][0]
                if cur_class:
                    # it's a method/nested def
                    f = Function(None, meth_name,
                                 lineno, meth_sig, modifierType=modifier)
                    cur_class._addmethod(meth_name, f)
            else:
                # it's a function
                f = Function(module, meth_name,
                             lineno, meth_sig, modifierType=modifier)
                if meth_name in dict_counts:
                    dict_counts[meth_name] += 1
                    meth_name = "{0}_{1:d}".format(
                        meth_name, dict_counts[meth_name])
                else:
                    dict_counts[meth_name] = 0
                dict[meth_name] = f
            classstack.append((f, thisindent))  # Marker for nested fns

            # reset the modifier settings
            modifierType = BaseClassBrowser.Function.General
            modifierIndent = -1

        elif m.start("String") >= 0:
            pass

        elif m.start("Class") >= 0:
            # we found a class definition
            thisindent = _indent(m.group("ClassIndent"))
            # close all classes indented at least as much
            while classstack and \
                    classstack[-1][1] >= thisindent:
                del classstack[-1]
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            class_name = m.group("ClassName")
            inherit = m.group("ClassSupers")
            if inherit:
                # the class inherits from other classes
                inherit = inherit[1:-1].strip()
                inherit = _commentsub('', inherit)
                names = []
                for n in inherit.split(','):
                    n = n.strip()
                    if n in dict:
                        # we know this super class
                        n = dict[n]
                    else:
                        c = n.split('.')
                        if len(c) > 1:
                            # super class
                            # is of the
                            # form module.class:
                            # look in
                            # module for class
                            m = c[-2]
                            c = c[-1]
                            if m in _modules:
                                d = _modules[m]
                                if c in d:
                                    n = d[c]
                    names.append(n)
                inherit = names
            # remember this class
            cur_class = Class(module, class_name, inherit, lineno)
            if not classstack:
                if class_name in dict_counts:
                    dict_counts[class_name] += 1
                    class_name = "{0}_{1:d}".format(
                        class_name, dict_counts[class_name])
                else:
                    dict_counts[class_name] = 0
                dict[class_name] = cur_class
            else:
                classstack[-1][0]._addclass(class_name, cur_class)
            classstack.append((cur_class, thisindent))

        elif m.start("Attribute") >= 0:
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            index = -1
            while index >= -len(classstack):
                if classstack[index][0] is not None and \
                   not isinstance(classstack[index][0], Function):
                    attr = Attribute(module, m.group("AttributeName"), lineno)
                    classstack[index][0]._addattribute(attr)
                    break
                else:
                    index -= 1

        elif m.start("Variable") >= 0:
            thisindent = _indent(m.group("VariableIndent"))
            variable_name = m.group("VariableName")
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            if thisindent == 0:
                # global variable
                if "@@Globals@@" not in dict:
                    dict["@@Globals@@"] = \
                        BaseClassBrowser.ClbrBase(module, "Globals", lineno)
                dict["@@Globals@@"]._addglobal(
                    Attribute(module, variable_name, lineno))
            else:
                index = -1
                while index >= -len(classstack):
                    if classstack[index][1] >= thisindent:
                        index -= 1
                    else:
                        if isinstance(classstack[index][0], Class):
                            classstack[index][0]._addglobal(
                                Attribute(module, variable_name, lineno))
                        break

        elif m.start("Publics") >= 0:
            idents = m.group("Identifiers")
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            pubs = Publics(module, lineno, idents)
            dict['__all__'] = pubs

        elif m.start("ConditionalDefine") >= 0:
            # a conditional function/method definition
            thisindent = _indent(m.group("ConditionalDefineIndent"))
            while conditionalsstack and \
                    conditionalsstack[-1] >= thisindent:
                del conditionalsstack[-1]
                if deltastack:
                    del deltastack[-1]
            conditionalsstack.append(thisindent)
            deltaindentcalculated = 0

        elif m.start("CodingLine") >= 0:
            # a coding statement
            coding = m.group("Coding")
            lineno = lineno + src.count('\n', last_lineno_pos, start)
            last_lineno_pos = start
            if "@@Coding@@" not in dict:
                dict["@@Coding@@"] = BaseClassBrowser.Coding(
                    module, lineno, coding)

        else:
            assert 0, "regexp _getnext found something unexpected"

    return dict


def _indent(ws):
    """
    Module function to return the indentation depth.

    @param ws the whitespace to be checked (string)
    @return length of the whitespace string (integer)
    """
    return len(ws.expandtabs(TABWIDTH))
