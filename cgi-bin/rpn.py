import operator as op
import math, re, random
from collections import namedtuple
import HTMLParser
import types, sys
from datetime import datetime

DEBUG = False
debug_log = open('./log','w') if DEBUG else None
def debug(msg):
    if DEBUG:
        if type(msg) == list:
            debug_log.write(' '.join([str(l) for l in msg])+'\n')
        else:
            debug_log.write(str(msg) + '\n')

# Cell types
CELL_NUM, CELL_STR, CELL_FUN = 0, 1, 2

# Forth data types
NUM, STR, FUN, REF = 0, 1, 2, 3

# Return status
ERROR, OK, DEFER = 0, 1, 2


# Function wrapper to support printing.
class Fn():
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn

    def __str__(self):
        return self.name

    def __call__(self, vm):
        return self.fn(vm)

class CtrlFn(Fn):
    def __call__(self, code, words, c_stack):
        return self.fn(code, words, c_stack)

class StackFn(Fn):
    def __call__(self, vm):
        try:
            self.fn(vm.s, vm.output)
        except Exception as e:
            vm.output.append("Err: "+ self.name +" " +str(e))

# Run-time functions
def swap(s, out):
    a = s.pop()
    b = s.pop()
    s.append(a)
    s.append(b)

def rot(s, out):
    a = s.pop()
    b = s.pop()
    c = s.pop()
    s.append(b), s.append(a), s.append(c)

def slice(s, out):
    end = int(s.pop())
    start = int(s.pop())
    data = s.pop()
    s.append(data[start:end])

def avg(s, out):
    v = s.pop()
    s.append(sum(v) / len(v))

def get_parameter_count(func):
    """Count parameter of a function.

    Supports Python functions (and built-in functions).
    If a function takes *args, then -1 is returned

    Example:
        import os
        arg = get_parameter_count(os.chdir)
        print(arg)  # Output: 1

    -- For C devs:
    In CPython, some built-in functions defined in C provide
    no metadata about their arguments. That's why we pass a
    list with 999 None objects (randomly choosen) to it and
    expect the underlying PyArg_ParseTuple fails with a
    corresponding error message.
    """

    # If the function is a builtin function we use our
    # approach. If it's an ordinary Python function we
    # fallback by using the the built-in extraction
    # functions (see else case), otherwise
    if isinstance(func, types.BuiltinFunctionType):
        try:
            arg_test = 999
            s = [None] * arg_test
            func(*s)
        except TypeError as e:
            message = str(e)
            found = re.match(
                r"[\w]+\(\) takes ([0-9]{1,3}) positional argument[s]* but " +
                str(arg_test) + " were given", message)
            if found:
                return int(found.group(1))

            if "takes no arguments" in message:
                return 0
            elif "takes at most" in message:
                found = re.match(
                    r"[\w]+\(\) takes at most ([0-9]{1,3}).+", message)
                if found:
                    return int(found.group(1))
            elif "takes exactly" in message:
                # string can contain 'takes 1' or 'takes one',
                # depending on the Python version
                found = re.match(
                    r"[\w]+\(\) takes exactly ([0-9]{1,3}|[\w]+).+", message)
                if found:
                    return 1 if found.group(1) == "one" \
                            else int(found.group(1))
        return -1  # *args
    else:
        try:
            if (sys.version_info > (3, 0)):
                argspec = inspect.getfullargspec(func)
            else:
                argspec = inspect.getargspec(func)
        except:
            raise TypeError("unable to determine parameter count")

        return -1 if argspec.varargs else len(argspec.args)

def call_python(method):
    def fun(s, out):
        if s:
            method 
            obj = s.pop()
            if hasattr(obj, method):
                fn = getattr(obj,method)
                n = get_parameter_count(fn)
                args = []
                for i in range(n):
                    args.append(s.pop())
                try:
                    s.append(fn(*args))
                except Exception as e:
                    out.append(str(e))
            else:
                out.append(
                    'Err: Invalid python call %s %s stack:%s'%(
                        str(obj),str(method), str(s)))
    return fun
            
def jmp(vm): return vm.code[vm.pc]

def jnz(vm): return (vm.code[vm.pc],vm.pc+1)[vm.s.pop()]

def jz(vm): return (vm.pc+1, vm.code[vm.pc])[vm.s.pop()==0]

def gt(s, out): b=s.pop(); a=s.pop(); s.append(int(a>b))
def lt(s, out): b=s.pop(); a=s.pop(); s.append(int(a<b))
def eq(s, out): b=s.pop(); a=s.pop(); s.append(int(a==b))

runtime_fn = {
    # Stack
    'dup': lambda s, out: s.append(s[-1]),
    'swap': swap,
    'drop': lambda s, out: s.pop(),
    'over': lambda s, out: s.append(s[-2]),
    'rot': rot,
    # String
    '.': lambda s, out: out.append(str(s.pop())),
    'cr': lambda s, out: out.append('\n'),
    'format': lambda s, out: s.append(str.format(s.pop(), s.pop())),
    # List
    'slice': slice,
    # Compare
    '>' : gt,
    '<' : lt,
    '=' : eq,
    # Math
    '+': lambda s, out: s.append(op.add(s.pop(-2), s.pop())),
    '-': lambda s, out: s.append(op.sub(s.pop(-2), s.pop())),
    '*': lambda s, out: s.append(op.mul(s.pop(-2), s.pop())),
    '/': lambda s, out: s.append(op.div(s.pop(-2), s.pop())),
    '^': lambda s, out: s.append(pow(s.pop(-2), s.pop())),
    'log': lambda s, out: s.append(math.log(s.pop(), s.pop())),
    'randint': lambda s, out: s.append(random.randint(s.pop(-2), s.pop())),
    'sqrt': lambda s, out: s.append(math.sqrt(s.pop())),
    'fabs': lambda s, out: s.append(math.fabs(s.pop())),
    'sin': lambda s, out: s.append(math.sin(s.pop())),
    'cos': lambda s, out: s.append(math.cos(s.pop())),
    'tan': lambda s, out: s.append(math.tan(s.pop())),
    'sum': lambda s, out: s.append(sum(s.pop())),
    'avg': avg,
    'int': lambda s, out: s.append(int(s.pop())),
    'float': lambda s, out: s.append(float(s.pop())),
    'str': lambda s, out: s.append(str(s.pop())),
    'strptime': lambda s, out: s.append(datetime.strptime(s.pop(), s.pop()))
}

# Compile-time functions
def colon(code, words, c_stack):
    if c_stack: return ': in ctrl stack', ERROR
    if words:
        label = words[0]
        del words[0]
        c_stack.append(("COLON", label))
    return 'Failed to get word.', ERROR

def semi(code, words, c_stack):
    if not c_stack: fatal("No : for ; to match")
    tag, label = c_stack.pop()
    if tag != "COLON": fatal(": not balanced with ;")
    user_ops[label.val] = code[:]  # Save word definition in rDict
    while code:
        code.pop()

def cIf(code, words, c_stack):
    code.append(Fn('jz',jz))
    c_stack.append(("IF", len(code)))
    code.append(0) # A placeholder for jump address

def cElse(code, words, c_stack):
    if not c_stack: return 'Failed to find matching IF', ERROR
    tag,slot = c_stack.pop()
    if tag != "IF": return 'Failed to find matching IF', ERROR
    code.append(Fn('jmp',jmp))
    c_stack.append(("ELSE", len(code)))
    code.append(0) # A placeholder for jump address
    code[slot] = len(code)

def cThen(code, words, c_stack):
    if not c_stack: return 'Failed to find matchign IF or ELSE', ERROR
    tag,slot = c_stack.pop()
    if tag not in ("IF", "ELSE"):
        return "THEN preceded by %s (not IF or ELSE)" % tag, ERROR
    code[slot] = len(code)

compile_fn = {':': CtrlFn(':', colon), ';': CtrlFn(';', semi), 'if': CtrlFn('if',cIf),
                  'else': CtrlFn('else',cElse), 'then': CtrlFn('then', cThen)}


# User defined words
user_ops = {}

# Store named tables on the page
tables = {}


def has_defer_ref(ref):
    if type(ref) == list:
        for v in ref:
            if has_defer_ref(v):
                return True
    else:
        cell_type, v = ref
        if cell_type == CELL_FUN:
            return True
    return False


def ref(t, row, col, table):
    global tables
    if '!' in t:
        t, remote = t.split('!')
        if remote in tables:
            ref_table = tables[remote]
        else:
            return 'Invalid reference (%s, @%s, $%s)' % (t, row, col), ERROR
    else:
        ref_table = table
    if not ref_table:
        return 'Invalid reference out of a table', ERROR
    crt_row = ref_table[row]
    rval = None
    if t.startswith('$'):
        rg = re.match('\$(-?\d+)\.\.\$(-?\d+)', t)
        if rg:
            start, end = int(rg.group(1)), int(rg.group(2))
            rval = [v for v in crt_row[start:end + 1]]
        else:
            if int(t[1:]) < len(crt_row):
                rval = crt_row[int(t[1:])]
    elif t.startswith('@'):
        rg = re.match(r'\@(-?\d+)\.\.\@(-?\d+)', t)
        row_col = re.match(r'\@(-?\d+)\$(-?\d+)', t)
        debug([t, rg, row_col])
        if rg:
            start = int(rg.group(1))
            start = start if start >= 0 else len(ref_table) + start
            end = int(rg.group(2))
            end = end  if end >= 0 else len(ref_table) + end 
            rval = [
                r[col] for i, r in enumerate(ref_table) if start <= i <= end
            ]
        elif row_col:
            t_row, t_col = int(row_col.group(1)), int(row_col.group(2))
            if t_row < len(ref_table) and t_col < len(ref_table[t_row]):
                rval = ref_table[t_row][t_col]
        else:
            target_row = int(t[1:])
            if (target_row < len(ref_table)):
                rval = table[target_row][col]
    if not rval:
        return 'invalid reference (%s, @%s, $%s)' % (t, row, col), ERROR
    if has_defer_ref(rval):
        return t, DEFER
    else:
        return rval, OK


# basic token container
Token = namedtuple("Token", ["tag", "val", "pos", "end"])


def tokenize2(text):
    """ Return tokens.

    >>> tokenize2('hello world')
    ([Token(tag=2, val='hello', pos=0, end=5), Token(tag=2, val='world', pos=6, end=11)], 1)
    >>> tokenize2('+ - * / ^ . ')
    ([Token(tag=2, val='+', pos=0, end=1), Token(tag=2, val='-', pos=2, end=3), Token(tag=2, val='*', pos=4, end=5), Token(tag=2, val='/', pos=6, end=7), Token(tag=2, val='^', pos=8, end=9), Token(tag=2, val='.', pos=10, end=11)], 1)
    >>> tokenize2('"hello" 1.7 -15 0.8 inc + - ')
    ([Token(tag=1, val='"hello"', pos=0, end=7), Token(tag=0, val='1.7', pos=8, end=11), Token(tag=0, val='-15', pos=12, end=15), Token(tag=0, val='0.8', pos=16, end=19), Token(tag=2, val='inc', pos=20, end=23), Token(tag=2, val='+', pos=24, end=25), Token(tag=2, val='-', pos=26, end=27)], 1)
    >>> tokenize2('@10 $10 @1..@10 $1..$10 @10$10')
    ([Token(tag=3, val='@10', pos=0, end=3), Token(tag=3, val='$10', pos=4, end=7), Token(tag=3, val='@1..@10', pos=8, end=15), Token(tag=3, val='$1..$10', pos=16, end=23), Token(tag=3, val='@10$10', pos=24, end=30)], 1)
    """

    text = HTMLParser.HTMLParser().unescape(text)
    rules = {
        "\"([^\"\\\\]|\\\\.)*\"": STR,
        "\'([^\'\\\\]|\\\\.)*\'": STR,
        r"[+-]?([0-9]*[.])?[0-9]+": NUM,
        r'[\w\+\-\*\/\^\.\:\;\=\>\<]+': FUN,
        r'[@|$][^ ]*': REF,
    }
    scanner_handler = lambda tag: lambda sc, val: Token(
        tag, val, sc.match.start(), sc.match.end())
    handlers = [(reg, scanner_handler(tag)) for (reg, tag) in rules.items()]
    handlers.append((r"\s+", None))
    toks, remain = re.Scanner(handlers).scan(text)
    if remain:
        return remain, ERROR
    return toks, OK


def compile(words, row=0, col=0, table=[]):
    code = []  # Compiled code
    c_stack = []  # Contrl Stack
    while words:
        word = words[0]
        words = words[1:]
        if word.tag == NUM:
            code.append(
                Fn('push_num:'+word.val, lambda vm, v=float(word.val): vm.s.append(v)))
        elif word.tag == STR:
            code.append(
                Fn('push_str:'+word.val,
                   lambda vm, v=word.val.strip('"\''): vm.s.append(v)))
        elif word.tag == FUN:
            if word.val in compile_fn:
                compile_fn[word.val](code, words, c_stack)
            elif word.val in user_ops:
                code.extend(user_ops[word.val])
            elif word.val in runtime_fn:
                code.append(StackFn(word.val, runtime_fn[word.val]))
            else:
                code.append(StackFn("Py:"+word.val, call_python(word.val)))
        elif word.tag == REF:
            rval, status = ref(word.val, row, col, table)
            debug([rval, status])
            if status == DEFER or status == ERROR:
                return '', status
            else:
                if type(rval) == list:
                    lst = [r[1] for r in rval]
                    code.append(
                        Fn('push_list', lambda vm, v=lst: vm.s.append(v)))
                elif rval[0] == CELL_NUM:
                    code.append(
                        Fn('push_num',
                           lambda vm, v=float(rval[1]): vm.s.append(v)))
                else:
                    code.append(
                        Fn('push_str',
                           lambda vm, v=rval[1].strip('"\''): vm.s.append(v)))
        else:
            return 'Invalid type:' + str(word), ERROR
        # print  ' '.join([str(c) for c in code])
    return code, OK


class VM():
    def __init__(self, code):
        self.s = []
        self.output = []
        self.pc = 0
        self.code = code

    def __str__(self):
        return 'vm s:%s pc:%d code:%s out:%s\n' % (str(
            self.s), self.pc, self.code[self.pc], str(self.output))

    def result(self):
        if self.output:
            return (CELL_STR, ''.join(self.output))
        if len(self.s) > 1:
            return (CELL_STR, str(self.s))
        if self.s:
            if type(self.s[0]) == int or type(self.s[0]) == float:
                return (CELL_NUM, self.s[0])
            else:
                return (CELL_STR, self.s[0])
        return (CELL_STR, '')

    def execute(self):
        while self.pc < len(self.code):
            #print ' '.join([str(v) for v in self.s])
            func = self.code[self.pc]
            self.pc += 1
            new_pc = func(self)
            if new_pc != None: self.pc = new_pc


def rpn_string(v):
    '''Evaluate a string.'''
    words, status = tokenize2(v)
    if status == ERROR:
        return "Fail to tokenize:" + v
    pcode, status = compile(words)
    if status != OK:
        return str(pcode)
    else:
        vm = VM(pcode)
        vm.execute()
        return str(vm.result()[1])

def rpn_table_vm(m):
    '''Evaluate a table.'''
    global tables
    table_env = []
    table = []
    max_iter = 3
    table_status = OK
    table_name = m.group(1)

    for row_i, row in enumerate(re.split('\|-', m.group(2))):
        table_env.append([])
        row_env = table_env[-1]
        for col_i, v in enumerate(map(str.strip,
                                      re.split('\|{1,2}', row)[1:])):
            if v.startswith('='):
                row_env.append((CELL_FUN, v[1:]))
            else:
                try:
                    value = float(v)
                    row_env.append((CELL_NUM, value))
                    continue
                except:
                    pass
                value = v
                row_env.append((CELL_STR, value))

    for cur_iter in range(max_iter):
        row_status = []
        for row_i, row in enumerate(table_env):
            for col_i, cell in enumerate(row):
                cell_type, cell_val = cell
                if cell_type == CELL_FUN:
                    toks, status = tokenize2(cell_val)
                    pcode, status = compile(toks, row_i, col_i, table_env)
                    if status == DEFER:
                        continue
                    elif status == ERROR:
                        table_env[row_i][col_i] = (CELL_STR, "Fail to compile" + pcode)
                    else:
                        vm = VM(pcode)
                        vm.execute()
                        table_env[row_i][col_i] = vm.result()
                elif cell_val and type(cell_val) == str and cell_val[0] in [
                        '@', '$'
                ]:
                    rval, status = ref(cell_val, row_i, col_i, table_env)
                    debug([rval,status])
                    if type(rval[1]) != list and status != DEFER:
                        table_env[row_i][col_i] = (rval[0], rval[1])
                else:
                    pass
        if any([s == DEFER for s in row_status]):
            continue
    if table_name:
        tables[table_name] = table_env
    for row_env in table_env:
        table.append('<tr><td>' +
                     '</td><td>'.join([str(v) for cell_type, v in row_env]) +
                     '</td></tr>')
    return '<table>' + '\n'.join(table) + '</table>'


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    p = '@1..@-2 '
    words, status = tokenize2(p)
    print words
    pcode, status = compile(words)
    print ' '.join([str(p) for p in pcode])
    if status != OK:
        print status
    else:
        vm = VM(pcode)
        vm.execute()
        print vm.result()
