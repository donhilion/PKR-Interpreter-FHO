from functools import reduce
from re import VERBOSE
from funcparserlib.lexer import make_tokenizer, Token
from funcparserlib.parser import some, with_forward_decls, many, a, skip

__author__ = 'Donhilion'

UNDEFINED = None

# leaves of the AST
class Leave(object):

    def eval(self, env):
        return UNDEFINED

class Variable(Leave):

    def __init__(self, name):
        self.name = name

    def eval(self, env):
        if self.name not in env:
            return UNDEFINED
        return env[self.name]

    def __str__(self):
        return "Variable(%s)" % self.name

class Const(Leave):

    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value

    def __str__(self):
        return "Const(%s)" % str(self.value)

class Add(Leave):
    
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, env):
        l = self.left.eval(env)
        if l == UNDEFINED: return UNDEFINED
        r = self.right.eval(env)
        if r == UNDEFINED: return UNDEFINED
        return l + r

    def __str__(self):
        return "Add(%s,%s)" % (str(self.left), str(self.right))

class Sub(Leave):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, env):
        l = self.left.eval(env)
        if l == UNDEFINED: return UNDEFINED
        r = self.right.eval(env)
        if r == UNDEFINED: return UNDEFINED
        return l - r

    def __str__(self):
        return "Sub(%s,%s)" % str(self.left), str(self.right)

class Mul(Leave):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, env):
        l = self.left.eval(env)
        if l == UNDEFINED: return UNDEFINED
        r = self.right.eval(env)
        if r == UNDEFINED: return UNDEFINED
        return l * r

    def __str__(self):
        return "Mul(%s,%s)" % (str(self.left), str(self.right))

class Div(Leave):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, env):
        l = self.left.eval(env)
        if l == UNDEFINED: return UNDEFINED
        r = self.right.eval(env)
        if r == UNDEFINED: return UNDEFINED
        if r == 0: return UNDEFINED
        return l / r

    def __str__(self):
        return "Div(%s,%s)" % (str(self.left), str(self.right))

class Eq(Leave):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, env):
        l = self.left.eval(env)
        if l == UNDEFINED: return UNDEFINED
        r = self.right.eval(env)
        if r == UNDEFINED: return UNDEFINED
        return l == r

    def __str__(self):
        return "Eq(%s,%s)" % (str(self.left), str(self.right))

class Gt(Leave):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, env):
        l = self.left.eval(env)
        if l == UNDEFINED: return UNDEFINED
        r = self.right.eval(env)
        if r == UNDEFINED: return UNDEFINED
        return l > r

    def __str__(self):
        return "Gt(%s,%s)" % (str(self.left), str(self.right))

class Lt(Leave):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, env):
        l = self.left.eval(env)
        if l == UNDEFINED: return UNDEFINED
        r = self.right.eval(env)
        if r == UNDEFINED: return UNDEFINED
        return l < r

    def __str__(self):
        return "Lt(%s,%s)" % (str(self.left), str(self.right))

class Let(Leave):

    def __init__(self, decls, exp):
        self.decls = decls
        self.exp = exp

    def eval(self, env):
        env_new = env.copy()
        for tup in self.decls:
            env_new[tup[0]] = tup[1].eval(env_new)
        return self.exp.eval(env_new)

    def __str__(self):
        return "Let(%s,%s)" % (str(self.decls), str(self.exp))

def tokenize(str):
    """Returns tokens of the given string."""
    specs = [
        ('Space',		(r'[ \t\r\n]+',)),
        ('True',		('true',)),
        ('False',		('false',)),
        ('If',  		('if',)),
        ('Then',		('then',)),
        ('Else',		('else',)),
        ('Fi',  		('fi',)),
        ('Call',		('call',)),
        ('Let', 		('let',)),
        ('In',  		('in',)),
        ('End', 		('end',)),
        ('Fun', 		('fun',)),
        ('Op',          (r'[\-+/*=<>]',)),
        ('Var', 		(r'[A-Za-z][A-Za-z_0-9]*',)),
        ('Number',      (r'(0|([1-9][0-9]*))', VERBOSE)),
        ('Semicolon',	(';',)),
        ]
    useless = ['Space']
    t = make_tokenizer(specs)
    return [x for x in t(str) if x.type not in useless]

def parse(seq):
    def eval_expr(z, list):
        return reduce(lambda s, (f, x): f(s, x), list, z)
    unarg = lambda f: lambda x: f(*x)
    tokval = lambda x: x.value # returns the value of a token
    toktype = lambda t: some(lambda x: x.type == t) >> tokval # checks type of token
    const = lambda x: lambda _: x # like ^^^ in Scala

    op = lambda s: a(Token('Op', s)) >> tokval # return the value if token is Op
    op_ = lambda s: skip(op(s)) # checks if token is Op and ignores it

    lst = lambda x: [x[0],] + x[1]
    tup = lambda x: (x[0], x[1])

    makeop = lambda s, f: op(s) >> const(f)

    add = makeop('+', Add)
    sub = makeop('-', Sub)
    mul = makeop('*', Mul)
    div = makeop('/', Div)

    operation = add | sub | mul | div

    decl = with_forward_decls(lambda:toktype('Var') + op_('=') + exp >> tup)
    decls = decl + many(skip(toktype('Semicolon') + decl)) >> lst
    e = toktype('Var') >> Variable | toktype('Number') >> (lambda x: Const(int(x))) |\
        toktype('True') >> (lambda x: Const(True)) | toktype('False') >> (lambda x: Const(False))
    exp = with_forward_decls(lambda:e + many(operation + e) >> unarg(eval_expr) |\
        skip(toktype('Let')) + decls + skip(toktype('In')) + exp + skip(toktype('End')) >> unarg(Let))

    return exp.parse(seq)

parsed = parse(tokenize("let x=3-1 in 1+x*3 end"))
print(parsed)
print(parsed.eval({}))