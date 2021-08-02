import operator as op;import math,re, random
unary_op=lambda t,s: t(s.pop())
two_op=lambda t,s: t(s.pop(-2),s.pop())
unary={'sqrt':math.sqrt, 'fabs':math.fabs, 'sin':math.sin, 'cos':math.cos,'tan':math.tan,
           'sum':sum, 'avg': lambda v: sum(v)/len(v), 'int':int, 'float':float, 'str': str}
def swap(s, out) : a=s.pop(); b=s.pop(); s.append(a); s.append(b)
def rot(s, out) :a=s.pop(); b=s.pop(); c=s.pop(); s.append(b), s.append(a), s.append(c)
def slice(s, out): end=int(s.pop());start=int(s.pop());data=s.pop(); s.append(data[start:end]) 
misc_fn={
    'dup': lambda s,out: s.append(s[-1]),
    'swap': swap,
    'drop': lambda s, out:s.pop(),
    'over': lambda s, out: s.append(s[-2]),
    'rot': rot,
    '.' : lambda s, out: out.append(str(s.pop())),
    'cr' : lambda s, out: out.append('\n'),
    'log': lambda s, out: math.log(s.pop(),s.pop()),
    'slice': slice,
    }

two={'+':op.add,'-':op.sub,'*':op.mul,'/':op.div,'^':pow, 'randint':random.randint}
ops=lambda t,s: unary_op(unary[t],s) if t in unary \
  else two_op(two[t],s) if t in two \
  else 'undefined function:' + t
user_ops = {}
def ref(t, col, env, table):
    if t.startswith('$'):
        rg = re.match('\$(\d+)\.\.\$(\d+)',t)
        if rg:
            start, end = int(rg.group(1)), int(rg.group(2))
            return [float(v) for v in env[start:end+1]]
        else:
            if int(t[1:]) < len(env):
                return env[int(t[1:])]
    elif t.startswith('@'):
        rg = re.match('\@(\d+)\.\.\@(\d+)',t)
        if rg:
            start, end = int(rg.group(1)), int(rg.group(2))
            return [float(r[col]) for i,r in enumerate(table) if start <= i <= end]
        else:
            row = int(t[1:])
            if (row < len(table)):
                return table[row][col]
    return 'invalid reference (%s, %s)' % (t, col)

def rpn(v,col=0, env=[],table=[]):
    global user_ops
    s=[]
    output=[]
    if v.startswith(':'):
        user_fn = v.strip(';').split()
        user_ops[user_fn[1]] = user_fn[2:]
        return ''
    def tokenize(v):
        STR, NON_STR, SP = 1, 2, 3
        state = SP
        t = []
        toks = []
        for i, c in enumerate(v):
            if state == SP:
                if c in ['"',"'"]:
                    state = STR
                elif c == " ":
                    continue
                else:
                    state = NON_STR
            if state == STR:
              t.append(c)
              if len(t) > 1 and c == t[0]:
                  toks.append(''.join(t))
                  t = []
                  state = SP
            if state == NON_STR:
                if c == ' ':
                    if t:
                        toks.append(''.join(t))
                        t = []
                        state = SP
                else:
                    t.append(c)
        if t:
            toks.append(''.join(t))
        return toks
    words=tokenize(v)
    try:
        while words:
            word = words[0]
            words = words[1:]
            if word !='.' and word != '-' and set(word).issubset(set("0123456789.-")):
                try: s.append(int(word))
                except:
                    try: s.append(float(word))
                    except:
                        s.append('failed to convert:'+word)
            elif word.startswith('"') or word.startswith("'"):
                s.append(word.strip('"\''))
            elif word in user_ops:
                words = user_ops[word] + words
            elif word.startswith('$') or word.startswith('@'):
                v = ref(word,col,env,table)
                try:
                    s.append(float(v))
                except:
                    s.append(v)
            elif word in misc_fn:
                rval = misc_fn[word](s,output)
                if rval:
                    s.append(rval)
            else:
                s.append(ops(word,s))
    except Exception as e:
        return 'err: %s %s %s'%(str(word),str(e), str(s))
    if output:
        return ''.join([str(o) for o in output])
    else:
        return str(s[0]) if len(s)==1 else str(s)
    

def rpn_row(row, table_env):
    env=[]
    for col, v in enumerate(map(str.strip,re.split('\|{1,2}',row)[1:])):
        env.append(str(v) if not v.startswith('=')
                       else rpn(v[1:],col,env,table_env))
    return env

def rpn_table(m):
    table_env=[]
    table = []
    for row in re.split('\|-',m.group(2)):
        row_env = rpn_row(row, table_env)
        table.append('<tr><td>'+'</td><td>'.join(row_env)+'</td></tr>')
        table_env.append(row_env)
    return '<table>'+'\n'.join(table)+'</table>'
