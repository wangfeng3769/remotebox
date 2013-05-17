__all__ = [
    "Template",
    "Render", "render", "frender",
    "ParseError", "SecurityError",
    "test"
]

import tokenize
import os
import glob
import re
from UserDict import DictMixin

from utils import storage, safeunicode, safestr, re_compile
from webapi import config
from net import websafe

def splitline(text):
    index = text.find('\n') + 1
    if index:
        return text[:index], text[index:]
    else:
        return text, ''

class Parser:
    def __init__(self):
        self.statement_nodes = STATEMENT_NODES
        self.keywords = KEYWORDS

    def parse(self, text, name="<template>"):
        self.text = text
        self.name = name
        
        defwith, text = self.read_defwith(text)
        suite = self.read_suite(text)
        return DefwithNode(defwith, suite)

    def read_defwith(self, text):
        if text.startswith('$def with'):
            defwith, text = splitline(text)
            defwith = defwith[1:].strip() # strip $ and spaces
            return defwith, text
        else:
            return '', text
    
    def read_section(self, text):
        if text.lstrip(' ').startswith('$'):
            index = text.index('$')
            begin_indent, text2 = text[:index], text[index+1:]
            ahead = self.python_lookahead(text2)
            
            if ahead == 'var':
                return self.read_var(text2)
            elif ahead in self.statement_nodes:
                return self.read_block_section(text2, begin_indent)
            elif ahead in self.keywords:
                return self.read_keyword(text2)
            elif ahead.strip() == '':
                # assignments starts with a space after $
                # ex: $ a = b + 2
                return self.read_assignment(text2)
        return self.readline(text)
        
    def read_var(self, text):
        line, text = splitline(text)
        tokens = self.python_tokens(line)
        if len(tokens) < 4:
            raise SyntaxError('Invalid var statement')
            
        name = tokens[1]
        sep = tokens[2]
        value = line.split(sep, 1)[1].strip()
        
        if sep == '=':
            pass # no need to process value
        elif sep == ':': 
            #@@ Hack for backward-compatability
            if tokens[3] == '\n': # multi-line var statement
                block, text = self.read_indented_block(text, '    ')
                lines = [self.readline(x)[0] for x in block.splitlines()]
                nodes = []
                for x in lines:
                    nodes.extend(x.nodes)
                    nodes.append(TextNode('\n'))         
            else: # single-line var statement
                linenode, _ = self.readline(value)
                nodes = linenode.nodes                
            parts = [node.emit('') for node in nodes]
            value = "join_(%s)" % ", ".join(parts)
        else:
            raise SyntaxError('Invalid var statement')
        return VarNode(name, value), text
                    
    def read_suite(self, text):
        sections = []
        while text:
            section, text = self.read_section(text)
            sections.append(section)
        return SuiteNode(sections)
    
    def readline(self, text):
        line, text = splitline(text)

        # supress new line if line ends with \
        if line.endswith('\\\n'):
            line = line[:-2]
                
        nodes = []
        while line:
            node, line = self.read_node(line)
            nodes.append(node)
            
        return LineNode(nodes), text

    def read_node(self, text):
        if text.startswith('$$'):
            return TextNode('$'), text[2:]
        elif text.startswith('$#'): # comment
            line, text = splitline(text)
            return TextNode('\n'), text
        elif text.startswith('$'):
            text = text[1:] # strip $
            if text.startswith(':'):
                escape = False
                text = text[1:] # strip :
            else:
                escape = True
            return self.read_expr(text, escape=escape)
        else:
            return self.read_text(text)
    
    def read_text(self, text):
        index = text.find('$')
        if index < 0:
            return TextNode(text), ''
        else:
            return TextNode(text[:index]), text[index:]
            
    def read_keyword(self, text):
        line, text = splitline(text)
        return StatementNode(line.strip() + "\n"), text

    def read_expr(self, text, escape=True):
        def simple_expr():
            identifier()
            extended_expr()
        
        def identifier():
            tokens.next()
        
        def extended_expr():
            lookahead = tokens.lookahead()
            if lookahead is None:
                return
            elif lookahead.value == '.':
                attr_access()
            elif lookahead.value in parens:
                paren_expr()
                extended_expr()
            else:
                return
        
        def attr_access():
            from token import NAME # python token constants
            dot = tokens.lookahead()
            if tokens.lookahead2().type == NAME:
                tokens.next() # consume dot
                identifier()
                extended_expr()
        
        def paren_expr():
            begin = tokens.next().value
            end = parens[begin]
            while True:
                if tokens.lookahead().value in parens:
                    paren_expr()
                else:
                    t = tokens.next()
                    if t.value == end:
                        break
            return

        parens = {
            "(": ")",
            "[": "]",
            "{": "}"
        }
        
        def get_tokens(text):
            readline = iter([text]).next
            end = None
            for t in tokenize.generate_tokens(readline):
                t = storage(type=t[0], value=t[1], begin=t[2], end=t[3])
                if end is not None and end != t.begin:
                    _, x1 = end
                    _, x2 = t.begin
                    yield storage(type=-1, value=text[x1:x2], begin=end, end=t.begin)
                end = t.end
                yield t
                
        class BetterIter:
            """Iterator like object with 2 support for 2 look aheads."""
            def __init__(self, items):
                self.iteritems = iter(items)
                self.items = []
                self.position = 0
                self.current_item = None
            
            def lookahead(self):
                if len(self.items) <= self.position:
                    self.items.append(self._next())
                return self.items[self.position]

            def _next(self):
                try:
                    return self.iteritems.next()
                except StopIteration:
                    return None
                
            def lookahead2(self):
                if len(self.items) <= self.position+1:
                    self.items.append(self._next())
                return self.items[self.position+1]
                    
            def next(self):
                self.current_item = self.lookahead()
                self.position += 1
                return self.current_item

        tokens = BetterIter(get_tokens(text))
                
        if tokens.lookahead().value in parens:
            paren_expr()
        else:
            simple_expr()
        row, col = tokens.current_item.end
        return ExpressionNode(text[:col], escape=escape), text[col:]    

    def read_assignment(self, text):
        r"""Reads assignment statement from text.
    
            >>> read_assignment = Parser().read_assignment
            >>> read_assignment('a = b + 1\nfoo')
            (<assignment: 'a = b + 1'>, 'foo')
        """
        line, text = splitline(text)
        return AssignmentNode(line.strip()), text
    
    def python_lookahead(self, text):
        readline = iter([text]).next
        tokens = tokenize.generate_tokens(readline)
        return tokens.next()[1]
        
    def python_tokens(self, text):
        readline = iter([text]).next
        tokens = tokenize.generate_tokens(readline)
        return [t[1] for t in tokens]
        
    def read_indented_block(self, text, indent):
        if indent == '':
            return '', text
            
        block = ""
        while text:
            line, text2 = splitline(text)
            if line.strip() == "":
                block += '\n'
            elif line.startswith(indent):
                block += line[len(indent):]
            else:
                break
            text = text2
        return block, text

    def read_statement(self, text):
        tok = PythonTokenizer(text)
        tok.consume_till(':')
        return text[:tok.index], text[tok.index:]
        
    def read_block_section(self, text, begin_indent=''):
        line, text = splitline(text)
        stmt, line = self.read_statement(line)
        keyword = self.python_lookahead(stmt)
        
        # if there is some thing left in the line
        if line.strip():
            block = line.lstrip()
        else:
            def find_indent(text):
                rx = re_compile('  +')
                match = rx.match(text)    
                first_indent = match and match.group(0)
                return first_indent or ""

            # find the indentation of the block by looking at the first line
            first_indent = find_indent(text)[len(begin_indent):]

            #TODO: fix this special case
            if keyword == "code":
                indent = begin_indent + first_indent
            else:
                indent = begin_indent + min(first_indent, INDENT)
            
            block, text = self.read_indented_block(text, indent)
            
        return self.create_block_node(keyword, stmt, block, begin_indent), text
        
    def create_block_node(self, keyword, stmt, block, begin_indent):
        if keyword in self.statement_nodes:
            return self.statement_nodes[keyword](stmt, block, begin_indent)
        else:
            raise ParseError, 'Unknown statement: %s' % repr(keyword)
        
class PythonTokenizer:
    """Utility wrapper over python tokenizer."""
    def __init__(self, text):
        self.text = text
        readline = iter([text]).next
        self.tokens = tokenize.generate_tokens(readline)
        self.index = 0
        
    def consume_till(self, delim):     
        try:
            while True:
                t = self.next()
                if t.value == delim:
                    break
                elif t.value == '(':
                    self.consume_till(')')
                elif t.value == '[':
                    self.consume_till(']')
                elif t.value == '{':
                    self.consume_till('}')

                # if end of line is found, it is an exception.
                # Since there is no easy way to report the line number,
                # leave the error reporting to the python parser later  
                #@@ This should be fixed.
                if t.value == '\n':
                    break
        except:
            #raise ParseError, "Expected %s, found end of line." % repr(delim)

            # raising ParseError doesn't show the line number. 
            # if this error is ignored, then it will be caught when compiling the python code.
            return
    
    def next(self):
        type, t, begin, end, line = self.tokens.next()
        row, col = end
        self.index = col
        return storage(type=type, value=t, begin=begin, end=end)
        
class DefwithNode:
    def __init__(self, defwith, suite):
        if defwith:
            self.defwith = defwith.replace('with', '__template__') + ':'
            # offset 4 lines. for encoding, __lineoffset__, loop and self.
            self.defwith += "\n    __lineoffset__ = -4"
        else:
            self.defwith = 'def __template__():'
            # offset 4 lines for encoding, __template__, __lineoffset__, loop and self.
            self.defwith += "\n    __lineoffset__ = -5"

        self.defwith += "\n    loop = ForLoop()"
        self.defwith += "\n    self = TemplateResult(); extend_ = self.extend"
        self.suite = suite
        self.end = "\n    return self"

    def emit(self, indent):
        encoding = "# coding: utf-8\n"
        return encoding + self.defwith + self.suite.emit(indent + INDENT) + self.end

    def __repr__(self):
        return "<defwith: %s, %s>" % (self.defwith, self.suite)

class TextNode:
    def __init__(self, value):
        self.value = value

    def emit(self, indent, begin_indent=''):
        return repr(safeunicode(self.value))
        
    def __repr__(self):
        return 't' + repr(self.value)

class ExpressionNode:
    def __init__(self, value, escape=True):
        self.value = value.strip()
        
        # convert ${...} to $(...)
        if value.startswith('{') and value.endswith('}'):
            self.value = '(' + self.value[1:-1] + ')'
            
        self.escape = escape

    def emit(self, indent, begin_indent=''):
        return 'escape_(%s, %s)' % (self.value, bool(self.escape))
        
    def __repr__(self):
        if self.escape:
            escape = ''
        else:
            escape = ':'
        return "$%s%s" % (escape, self.value)
        
class AssignmentNode:
    def __init__(self, code):
        self.code = code
        
    def emit(self, indent, begin_indent=''):
        return indent + self.code + "\n"
        
    def __repr__(self):
        return "<assignment: %s>" % repr(self.code)
        
class LineNode:
    def __init__(self, nodes):
        self.nodes = nodes
        
    def emit(self, indent, text_indent='', name=''):
        text = [node.emit('') for node in self.nodes]
        if text_indent:
            text = [repr(text_indent)] + text

        return indent + "extend_([%s])\n" % ", ".join(text)        
    
    def __repr__(self):
        return "<line: %s>" % repr(self.nodes)

INDENT = '    ' # 4 spaces
        
class BlockNode:
    def __init__(self, stmt, block, begin_indent=''):
        self.stmt = stmt
        self.suite = Parser().read_suite(block)
        self.begin_indent = begin_indent

    def emit(self, indent, text_indent=''):
        text_indent = self.begin_indent + text_indent
        out = indent + self.stmt + self.suite.emit(indent + INDENT, text_indent)
        return out
        
    def __repr__(self):
        return "<block: %s, %s>" % (repr(self.stmt), repr(self.suite))

class ForNode(BlockNode):
    def __init__(self, stmt, block, begin_indent=''):
        self.original_stmt = stmt
        tok = PythonTokenizer(stmt)
        tok.consume_till('in')
        a = stmt[:tok.index] # for i in
        b = stmt[tok.index:-1] # rest of for stmt excluding :
        stmt = a + ' loop.setup(' + b.strip() + '):'
        BlockNode.__init__(self, stmt, block, begin_indent)
        
    def __repr__(self):
        return "<block: %s, %s>" % (repr(self.original_stmt), repr(self.suite))

class CodeNode:
    def __init__(self, stmt, block, begin_indent=''):
        # compensate one line for $code:
        self.code = "\n" + block
        
    def emit(self, indent, text_indent=''):
        import re
        rx = re.compile('^', re.M)
        return rx.sub(indent, self.code).rstrip(' ')
        
    def __repr__(self):
        return "<code: %s>" % repr(self.code)
        
class StatementNode:
    def __init__(self, stmt):
        self.stmt = stmt
        
    def emit(self, indent, begin_indent=''):
        return indent + self.stmt
        
    def __repr__(self):
        return "<stmt: %s>" % repr(self.stmt)
        
class IfNode(BlockNode):
    pass

class ElseNode(BlockNode):
    pass

class ElifNode(BlockNode):
    pass

class DefNode(BlockNode):
    def __init__(self, *a, **kw):
        BlockNode.__init__(self, *a, **kw)

        code = CodeNode("", "")
        code.code = "self = TemplateResult(); extend_ = self.extend\n"
        self.suite.sections.insert(0, code)

        code = CodeNode("", "")
        code.code = "return self\n"
        self.suite.sections.append(code)
        
    def emit(self, indent, text_indent=''):
        text_indent = self.begin_indent + text_indent
        out = indent + self.stmt + self.suite.emit(indent + INDENT, text_indent)
        return indent + "__lineoffset__ -= 3\n" + out

class VarNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def emit(self, indent, text_indent):
        return indent + "self[%s] = %s\n" % (repr(self.name), self.value)
        
    def __repr__(self):
        return "<var: %s = %s>" % (self.name, self.value)

class SuiteNode:
    """Suite is a list of sections."""
    def __init__(self, sections):
        self.sections = sections
        
    def emit(self, indent, text_indent=''):
        return "\n" + "".join([s.emit(indent, text_indent) for s in self.sections])
        
    def __repr__(self):
        return repr(self.sections)

STATEMENT_NODES = {
    'for': ForNode,
    'while': BlockNode,
    'if': IfNode,
    'elif': ElifNode,
    'else': ElseNode,
    'def': DefNode,
    'code': CodeNode
}

KEYWORDS = [
    "pass",
    "break",
    "continue",
    "return"
]

TEMPLATE_BUILTIN_NAMES = [
    "dict", "enumerate", "float", "int", "bool", "list", "long", "reversed", 
    "set", "slice", "tuple", "xrange",
    "abs", "all", "any", "callable", "chr", "cmp", "divmod", "filter", "hex", 
    "id", "isinstance", "iter", "len", "max", "min", "oct", "ord", "pow", "range",
    "True", "False",
    "None",
    "__import__", # some c-libraries like datetime requires __import__ to present in the namespace
]

import __builtin__
TEMPLATE_BUILTINS = dict([(name, getattr(__builtin__, name)) for name in TEMPLATE_BUILTIN_NAMES if name in __builtin__.__dict__])

class ForLoop:
    def __init__(self):
        self._ctx = None
        
    def __getattr__(self, name):
        if self._ctx is None:
            raise AttributeError, name
        else:
            return getattr(self._ctx, name)
        
    def setup(self, seq):        
        self._push()
        return self._ctx.setup(seq)
        
    def _push(self):
        self._ctx = ForLoopContext(self, self._ctx)
        
    def _pop(self):
        self._ctx = self._ctx.parent
                
class ForLoopContext:
    def __init__(self, forloop, parent):
        self._forloop = forloop
        self.parent = parent
        
    def setup(self, seq):
        try:
            self.length = len(seq)
        except:
            self.length = 0

        self.index = 0
        for a in seq:
            self.index += 1
            yield a
        self._forloop._pop()
            
    index0 = property(lambda self: self.index-1)
    first = property(lambda self: self.index == 1)
    last = property(lambda self: self.index == self.length)
    odd = property(lambda self: self.index % 2 == 1)
    even = property(lambda self: self.index % 2 == 0)
    parity = property(lambda self: ['odd', 'even'][self.even])
    revindex0 = property(lambda self: self.length - self.index)
    revindex = property(lambda self: self.length - self.index + 1)
        
class BaseTemplate:
    def __init__(self, code, filename, filter, globals, builtins):
        self.filename = filename
        self.filter = filter
        self._globals = globals
        self._builtins = builtins
        if code:
            self.t = self._compile(code)
        else:
            self.t = lambda: ''
        
    def _compile(self, code):
        env = self.make_env(self._globals or {}, self._builtins)
        exec(code, env)
        return env['__template__']

    def __call__(self, *a, **kw):
        __hidetraceback__ = True
        return self.t(*a, **kw)

    def make_env(self, globals, builtins):
        return dict(globals,
            __builtins__=builtins, 
            ForLoop=ForLoop,
            TemplateResult=TemplateResult,
            escape_=self._escape,
            join_=self._join
        )
    def _join(self, *items):
        return u"".join(items)
            
    def _escape(self, value, escape=False):
        if value is None: 
            value = ''
            
        value = safeunicode(value)
        if escape and self.filter:
            value = self.filter(value)
        return value

class Template(BaseTemplate):
    CONTENT_TYPES = {
        '.html' : 'text/html; charset=utf-8',
        '.xhtml' : 'application/xhtml+xml; charset=utf-8',
        '.txt' : 'text/plain',
    }
    FILTERS = {
        '.html': websafe,
        '.xhtml': websafe,
        '.xml': websafe
    }
    globals = {}
    
    def __init__(self, text, filename='<template>', filter=None, globals=None, builtins=None, extensions=None):
        self.extensions = extensions or []
        text = Template.normalize_text(text)
        code = self.compile_template(text, filename)
                
        _, ext = os.path.splitext(filename)
        filter = filter or self.FILTERS.get(ext, None)
        self.content_type = self.CONTENT_TYPES.get(ext, None)

        if globals is None:
            globals = self.globals
        if builtins is None:
            builtins = TEMPLATE_BUILTINS
                
        BaseTemplate.__init__(self, code=code, filename=filename, filter=filter, globals=globals, builtins=builtins)
        
    def normalize_text(text):
        """Normalizes template text by correcting \r\n, tabs and BOM chars."""
        text = text.replace('\r\n', '\n').replace('\r', '\n').expandtabs()
        if not text.endswith('\n'):
            text += '\n'

        # ignore BOM chars at the begining of template
        BOM = '\xef\xbb\xbf'
        if isinstance(text, str) and text.startswith(BOM):
            text = text[len(BOM):]
        
        # support fort \$ for backward-compatibility 
        text = text.replace(r'\$', '$$')
        return text
    normalize_text = staticmethod(normalize_text)
                
    def __call__(self, *a, **kw):
        __hidetraceback__ = True
        import webapi as web
        if 'headers' in web.ctx and self.content_type:
            web.header('Content-Type', self.content_type, unique=True)
            
        return BaseTemplate.__call__(self, *a, **kw)
        
    def generate_code(text, filename, parser=None):
        # parse the text
        parser = parser or Parser()
        rootnode = parser.parse(text, filename)
                
        # generate python code from the parse tree
        code = rootnode.emit(indent="").strip()
        return safestr(code)
        
    generate_code = staticmethod(generate_code)
    
    def create_parser(self):
        p = Parser()
        for ext in self.extensions:
            p = ext(p)
        return p
                
    def compile_template(self, template_string, filename):
        code = Template.generate_code(template_string, filename, parser=self.create_parser())

        def get_source_line(filename, lineno):
            try:
                lines = open(filename).read().splitlines()
                return lines[lineno]
            except:
                return None
        
        try:
            # compile the code first to report the errors, if any, with the filename
            compiled_code = compile(code, filename, 'exec')
        except SyntaxError, e:
            # display template line that caused the error along with the traceback.
            try:
                e.msg += '\n\nTemplate traceback:\n    File %s, line %s\n        %s' % \
                    (repr(e.filename), e.lineno, get_source_line(e.filename, e.lineno-1))
            except: 
                pass
            raise
        
        # make sure code is safe
        import compiler
        ast = compiler.parse(code)
        SafeVisitor().walk(ast, filename)

        return compiled_code
        
class CompiledTemplate(Template):
    def __init__(self, f, filename):
        Template.__init__(self, '', filename)
        self.t = f
        
    def compile_template(self, *a):
        return None
    
    def _compile(self, *a):
        return None
                
class Render:
    def __init__(self, loc='templates', cache=None, base=None, **keywords):
        self._loc = loc
        self._keywords = keywords

        if cache is None:
            cache = not config.get('debug', False)
        
        if cache:
            self._cache = {}
        else:
            self._cache = None
        
        if base and not hasattr(base, '__call__'):
            # make base a function, so that it can be passed to sub-renders
            self._base = lambda page: self._template(base)(page)
        else:
            self._base = base
    
    def _add_global(self, obj, name=None):
        """Add a global to this rendering instance."""
        if 'globals' not in self._keywords: self._keywords['globals'] = {}
        if not name:
            name = obj.__name__
        self._keywords['globals'][name] = obj
    
    def _lookup(self, name):
        path = os.path.join(self._loc, name)
        if os.path.isdir(path):
            return 'dir', path
        else:
            path = self._findfile(path)
            if path:
                return 'file', path
            else:
                return 'none', None
        
    def _load_template(self, name):
        kind, path = self._lookup(name)
        
        if kind == 'dir':
            return Render(path, cache=self._cache is not None, base=self._base, **self._keywords)
        elif kind == 'file':
            return Template(open(path).read(), filename=path, **self._keywords)
        else:
            raise AttributeError, "No template named " + name  
        
    def loadTemplateByPath(self,path): 
         #self.pathR=True
         return Template(open(path).read(), filename=path, **self._keywords)         

    def _findfile(self, path_prefix): 
        p = [f for f in glob.glob(path_prefix + '.*') if not f.endswith('~')] # skip backup files
        p.sort() # sort the matches for deterministic order
        return p and p[0]
            
    def _template(self, name):
        if self._cache is not None:
            if name not in self._cache:
                self._cache[name] = self._load_template(name)
            return self._cache[name]
        else:
            return self._load_template(name)
        
    def __getattr__(self, name):
        t = self._template(name)
        if self._base and isinstance(t, Template):
            def template(*a, **kw):
                return self._base(t(*a, **kw))
            return template
        else:
            return self._template(name)

class GAE_Render(Render):
    # Render gets over-written. make a copy here.
    super = Render
    def __init__(self, loc, *a, **kw):
        GAE_Render.super.__init__(self, loc, *a, **kw)
        
        import types
        if isinstance(loc, types.ModuleType):
            self.mod = loc
        else:
            name = loc.rstrip('/').replace('/', '.')
            self.mod = __import__(name, None, None, ['x'])

        self.mod.__dict__.update(kw.get('builtins', TEMPLATE_BUILTINS))
        self.mod.__dict__.update(Template.globals)
        self.mod.__dict__.update(kw.get('globals', {}))

    def _load_template(self, name):
        t = getattr(self.mod, name)
        import types
        if isinstance(t, types.ModuleType):
            return GAE_Render(t, cache=self._cache is not None, base=self._base, **self._keywords)
        else:
            return t

render = Render
# setup render for Google App Engine.
try:
    from google import appengine
    render = Render = GAE_Render
except ImportError:
    pass
        
def frender(path, **keywords):
    """Creates a template from the given file path.
    """
    return Template(open(path).read(), filename=path, **keywords)
    
def compile_templates(root):
    """Compiles templates to python code."""
    re_start = re_compile('^', re.M)
    
    for dirpath, dirnames, filenames in os.walk(root):
        filenames = [f for f in filenames if not f.startswith('.') and not f.endswith('~') and not f.startswith('__init__.py')]

        for d in dirnames[:]:
            if d.startswith('.'):
                dirnames.remove(d) # don't visit this dir

        out = open(os.path.join(dirpath, '__init__.py'), 'w')
        out.write('from web.template import CompiledTemplate, ForLoop, TemplateResult\n\n')
        if dirnames:
            out.write("import " + ", ".join(dirnames))
        out.write("\n")

        for f in filenames:
            path = os.path.join(dirpath, f)

            if '.' in f:
                name, _ = f.split('.', 1)
            else:
                name = f
                
            text = open(path).read()
            text = Template.normalize_text(text)
            code = Template.generate_code(text, path)

            code = code.replace("__template__", name, 1)
            
            out.write(code)

            out.write('\n\n')
            out.write('%s = CompiledTemplate(%s, %s)\n' % (name, name, repr(path)))
            out.write("join_ = %s._join; escape_ = %s._escape\n\n" % (name, name))

            # create template to make sure it compiles
            t = Template(open(path).read(), path)
        out.close()
                
class ParseError(Exception):
    pass
    
class SecurityError(Exception):
    """The template seems to be trying to do something naughty."""
    pass

# Enumerate all the allowed AST nodes
ALLOWED_AST_NODES = [
    "Add", "And",
#   "AssAttr",
    "AssList", "AssName", "AssTuple",
#   "Assert",
    "Assign", "AugAssign",
#   "Backquote",
    "Bitand", "Bitor", "Bitxor", "Break",
    "CallFunc","Class", "Compare", "Const", "Continue",
    "Decorators", "Dict", "Discard", "Div",
    "Ellipsis", "EmptyNode",
#   "Exec",
    "Expression", "FloorDiv", "For",
#   "From",
    "Function", 
    "GenExpr", "GenExprFor", "GenExprIf", "GenExprInner",
    "Getattr", 
#   "Global", 
    "If", "IfExp",
#   "Import",
    "Invert", "Keyword", "Lambda", "LeftShift",
    "List", "ListComp", "ListCompFor", "ListCompIf", "Mod",
    "Module",
    "Mul", "Name", "Not", "Or", "Pass", "Power",
#   "Print", "Printnl", "Raise",
    "Return", "RightShift", "Slice", "Sliceobj",
    "Stmt", "Sub", "Subscript",
#   "TryExcept", "TryFinally",
    "Tuple", "UnaryAdd", "UnarySub",
    "While", "With", "Yield",
]

class SafeVisitor(object):
    def __init__(self):
        "Initialize visitor by generating callbacks for all AST node types."
        self.errors = []

    def walk(self, ast, filename):
        "Validate each node in AST and raise SecurityError if the code is not safe."
        self.filename = filename
        self.visit(ast)
        
        if self.errors:        
            raise SecurityError, '\n'.join([str(err) for err in self.errors])
        
    def visit(self, node, *args):
        "Recursively validate node and all of its children."
        def classname(obj):
            return obj.__class__.__name__
        nodename = classname(node)
        fn = getattr(self, 'visit' + nodename, None)
        
        if fn:
            fn(node, *args)
        else:
            if nodename not in ALLOWED_AST_NODES:
                self.fail(node, *args)
            
        for child in node.getChildNodes():
            self.visit(child, *args)

    def visitName(self, node, *args):
        "Disallow any attempts to access a restricted attr."
        #self.assert_attr(node.getChildren()[0], node)
        pass
        
    def visitGetattr(self, node, *args):
        "Disallow any attempts to access a restricted attribute."
        self.assert_attr(node.attrname, node)
            
    def assert_attr(self, attrname, node):
        if self.is_unallowed_attr(attrname):
            lineno = self.get_node_lineno(node)
            e = SecurityError("%s:%d - access to attribute '%s' is denied" % (self.filename, lineno, attrname))
            self.errors.append(e)

    def is_unallowed_attr(self, name):
        return name.startswith('_') \
            or name.startswith('func_') \
            or name.startswith('im_')
            
    def get_node_lineno(self, node):
        return (node.lineno) and node.lineno or 0
        
    def fail(self, node, *args):
        "Default callback for unallowed AST nodes."
        lineno = self.get_node_lineno(node)
        nodename = node.__class__.__name__
        e = SecurityError("%s:%d - execution of '%s' statements is denied" % (self.filename, lineno, nodename))
        self.errors.append(e)

class TemplateResult(storage, DictMixin):
    def __init__(self, *a, **kw):
        storage.__init__(self, *a, **kw)
        self.setdefault("__body__", None)

        # avoiding self._data because it adds as item instead of attr.
        self.__dict__["_data"] = []
        self.__dict__["extend"] = self._data.extend

    def __getitem__(self, name):
        if name == "__body__" and storage.__getitem__(self, '__body__') is None:
            self["__body__"] = u"".join(self._data)
        return storage.__getitem__(self, name)

    def __unicode__(self): 
        return self["__body__"]
    
    def __str__(self):
        return self["__body__"].encode('utf-8')
        
    def __repr__(self):
        self["__body__"] # initialize __body__ if not already initialized
        return "<TemplateResult: %s>" % dict.__repr__(self)

def test():
    pass
            
if __name__ == "__main__":
    import sys
    if '--compile' in sys.argv:
        compile_templates(sys.argv[2])
    else:
        import doctest
        doctest.testmod()
