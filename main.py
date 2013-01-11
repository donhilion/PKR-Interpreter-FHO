from functools import reduce
from re import VERBOSE
from funcparserlib.lexer import make_tokenizer, Token
from funcparserlib.parser import some, with_forward_decls, many, a, skip, maybe
import programs

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

    def get_name(self):
        return self.name

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
        return "Sub(%s,%s)" % (str(self.left), str(self.right))

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
        return int(l / r)

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
        decls = ""
        for decl in self.decls:
            decls += "%s = %s," % (str(decl[0]), str(decl[1]))
        return "Let(%s,%s)" % (decls[:-1], str(self.exp))

class If(Leave):

    def __init__(self, cond, the, els):
        self.cond = cond
        self.the = the
        self.els = els

    def eval(self, env):
        cond = self.cond.eval(env)
        if cond == UNDEFINED:
            return UNDEFINED
        if cond:
            return self.the.eval(env)
        if self.els is not None:
            return self.els.eval(env)
        return UNDEFINED

    def __str__(self):
        return "If(%s then %s else %s)" % (str(self.cond), str(self.the), str(self.els))

class Fun(Leave):

    def __init__(self, vars, exp):
        self.vars = vars
        self.exp = exp
        self.env = None

    def eval(self, env):
        if self.env is None:
            self.env = env
        return self

    def call(self, env, args):
        if len(args) != len(self.vars):
            return UNDEFINED
        tuples = zip(self.vars, args)
        env_new = self.env.copy()
        for tup in tuples:
            env_new[tup[0].get_name()] = tup[1].eval(env)
        return self.exp.eval(env_new)

    def __str__(self):
        vars = ""
        for var in self.vars:
            vars += "%s," % (str(var),)
        return "Fun(%s => %s)" % (vars[:-1], str(self.exp))

class Call(Leave):

    def __init__(self, fun, args):
        self.fun = fun
        self.args = args

    def eval(self, env):
        fun = self.fun.eval(env)
        if fun is UNDEFINED:
            return UNDEFINED
        return fun.call(env, self.args)

    def __str__(self):
        args = ""
        for arg in self.args:
            args += "%s," % (str(arg),)
        return "Call(%s (%s))" % (str(self.fun), args[:-1])

class Prog(Leave):

    def __init__(self, exp):
        self.exp = exp

    def eval(self, env):
        return self.exp.eval(env)

    def __str__(self):
        return "Prog(%s)" % str(self.exp)

    def run(self):
        return self.eval({})

def tokenize(str):
    """
    Generates a list of tokens from the given string.
    """
    specs = [
        ('Space',		(r'[ \t\r\n]+',)),
        ('True',		('true',)),
        ('False',		('false',)),
        ('If',  		('if',)),
        ('Then',		('then',)),
        ('Else',		('else',)),
        ('Fi',  		('fi',)),
        ('Call',		('call',)),
        ('Lp',  		('\(',)),
        ('Comma',  		(',',)),
        ('Rp',  		('\)',)),
        ('Let', 		('let',)),
        ('In',  		('in',)),
        ('End', 		('end',)),
        ('Fun', 		('fun',)),
        ('Arrow', 		('=>',)),
        ('Prog',    	('prog',)),
        ('Op',          (r'[\-+/*=<>]',)),
        ('Var', 		(r'[A-Za-z][A-Za-z_0-9]*',)),
        ('Number',      (r'(0|([1-9][0-9]*))', VERBOSE)),
        ('Semicolon',	(';',)),
        ]
    useless = ['Space']
    t = make_tokenizer(specs)
    return [x for x in t(str) if x.type not in useless]

def parse(seq):
    """
    Parses the list of tokens and generates an AST.
    """
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

    lt = makeop('<', Lt)
    gt = makeop('>', Gt)
    eq = makeop('=', Eq)

    operation = add | sub | mul | div | lt | gt | eq

    decl = with_forward_decls(lambda:toktype('Var') + op_('=') + (exp | fun) >> tup)
    decls = decl + many(skip(toktype('Semicolon')) + decl) >> lst
    variable = toktype('Var') >> Variable
    variables = variable + many(skip(toktype('Comma')) + variable) >> lst
    fun = with_forward_decls(lambda: skip(toktype('Fun')) + variables + skip(toktype('Arrow')) + exp + skip(toktype('End'))) >> unarg(Fun)
    parameters = with_forward_decls(lambda: exp + many(skip(toktype('Comma')) + exp) >> lst)
    call = skip(toktype('Call')) + (fun | variable) + skip(toktype('Lp')) + parameters + skip(toktype('Rp')) >> unarg(Call)
    ex = with_forward_decls(lambda:variable | toktype('Number') >> (lambda x: Const(int(x))) |\
        toktype('True') >> (lambda x: Const(True)) | toktype('False') >> (lambda x: Const(False)) |\
        skip(toktype('Let')) + decls + skip(toktype('In')) + exp + skip(toktype('End')) >> unarg(Let) |\
        skip(toktype('If')) + exp + skip(toktype('Then')) + exp + maybe(skip(toktype('Else')) + exp) + skip(toktype('Fi')) >> unarg(If) |\
        fun | call)
    exp = ex + many(operation + ex) >> unarg(eval_expr)
    prog = skip(toktype('Prog')) + exp >> Prog

    return prog.parse(seq)

parsed = parse(tokenize(programs.factorial))
print(parsed)
print(parsed.run())

parsed = parse(tokenize(programs.fibonacci))
print(parsed)
print(parsed.run())

parsed = parse(tokenize(programs.square))
print(parsed)
print(parsed.run())

parsed = parse(tokenize(programs.exp))
print(parsed)
print(parsed.run())

parsed = parse(tokenize(programs.vars))
print(parsed)
print(parsed.run())

parsed = parse(tokenize(programs.stat))
print(parsed)
print(parsed.run())

parsed = parse(tokenize(programs.high))
print(parsed)
print(parsed.run())