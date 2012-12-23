from functools import reduce
from re import VERBOSE
from funcparserlib.lexer import make_tokenizer, Token
from funcparserlib.parser import some, with_forward_decls, many, a, skip, maybe

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
        if self.els != None:
            return self.els.eval(env)
        return UNDEFINED

    def __str__(self):
        return "If(%s then %s else %s)" % (str(self.cond), str(self.the), str(self.els))

class Fun(Leave):

    def __init__(self, vars, exp):
        self.vars = vars
        self.exp = exp

    def eval(self, env):
        return self

    def call(self, env, args):
        if len(args) < len(self.vars):
            return UNDEFINED
        tuples = zip(self.vars, args)
        env_new = env.copy()
        for tup in tuples:
            env_new[tup[0].get_name()] = tup[1].eval(env_new)
        return self.exp.eval(env_new)

    def __str__(self):
        return "Fun(%s => %s)" % (str(self.vars), str(self.exp))

class Call(Leave):

    def __init__(self, fun, args):
        self.fun = fun
        self.args = args

    def eval(self, env):
        return self.fun.eval(env).call(env, self.args)

    def __str__(self):
        return "Call(%s (%s))" % (str(self.fun), str(self.args))

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
        ('Lp',  		('\(',)),
        ('Comma',  		(',',)),
        ('Rp',  		('\)',)),
        ('Let', 		('let',)),
        ('In',  		('in',)),
        ('End', 		('end',)),
        ('Fun', 		('fun',)),
        ('Arrow', 		('=>',)),
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

    decl = with_forward_decls(lambda:toktype('Var') + op_('=') + (exp | fun) >> tup)
    decls = decl + many(skip(toktype('Semicolon')) + decl) >> lst
    variable = toktype('Var') >> Variable
    variables = variable + many(variable) >> lst
    fun = with_forward_decls(lambda: skip(toktype('Fun')) + variables + skip(toktype('Arrow')) + exp + skip(toktype('End'))) >> unarg(Fun)
    parameters = with_forward_decls(lambda: exp + many(skip(toktype('Comma')) + exp) >> lst)
    call = skip(toktype('Call')) + (fun | variable) + skip(toktype('Lp')) + parameters + skip(toktype('Rp')) >> unarg(Call)
    ex = with_forward_decls(lambda:variable | toktype('Number') >> (lambda x: Const(int(x))) |\
        toktype('True') >> (lambda x: Const(True)) | toktype('False') >> (lambda x: Const(False)) |\
        skip(toktype('Let')) + decls + skip(toktype('In')) + exp + skip(toktype('End')) >> unarg(Let) |\
        skip(toktype('If')) + exp + skip(toktype('Then')) + exp + maybe(skip(toktype('Else')) + exp) + skip(toktype('Fi')) >> unarg(If) |\
        fun | call)
    exp = ex + op_('<') + ex >> unarg(Lt) | ex + op_('>') + ex >> unarg(Gt) | ex + op_('=') + ex >> unarg(Eq) |\
        ex + many(operation + ex) >> unarg(eval_expr)

    return exp.parse(seq)

#parsed = parse(tokenize("let f1 = fun a b c => if a then 1+b*c fi end in call f1(false,2,3) end"))
#parsed = parse(tokenize("let y=fun a => a * 2 end in call y(1) end"))
parsed = parse(tokenize("let fac=fun a => if a>0 then a*call fac(a-1) else 1 fi end in call fac(4) end"))
print(parsed)
print(parsed.eval({}))