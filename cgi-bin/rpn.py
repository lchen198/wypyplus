import operator as op;import math,re
unary_op=lambda t,s: t(s.pop())
norm_op=lambda t,s: t(s.pop(-2),s.pop())
rev_op=lambda t,s: t(s.pop(),s.pop())
unary={'sqrt':math.sqrt, 'fabs':math.fabs, 'sin':math.sin, 'cos':math.cos,'tan':math.tan,
           'sum':sum, 'avg': lambda v: sum(v)/len(v)}
def swap(s) : a=s.pop(); b=s.pop(); s.append(a); s.append(b)
def rot(s) :a=s.pop(); b=s.pop(); c=s.pop(); s.append(b), s.append(a), s.append(c)
stack={'dup': lambda s: s.append(s[-1]), 'swap': swap, 'drop': lambda s:s.pop(),
  'over': lambda s: s.append(s[-2]), 'rot': rot}

norm={'+':op.add,'-':op.sub,'*':op.mul,'/':op.div,'^':pow}
rev={'log':math.log};
ops=lambda t,s: unary_op(unary[t],s) if t in unary \
  else norm_op(norm[t],s) if t in norm \
  else rev_op(rev[t],s) if t in rev \
  else 'undefined function:' + t
user_ops = {}
log = open('./log','a')
def ref(t, col, env, table):
    if t.startswith('$'):
        rg = re.match('\$(\d+)\.\.\$(\d+)',t)
        if rg:
            start, end = int(rg.group(1)), int(rg.group(2))
            return [float(v) for v in env[start:end+1]]
        else:
            if int(t[1:]) < len(env):
                return float(env[int(t[1:])] or 0 )
    elif t.startswith('@'):
        rg = re.match('\@(\d+)\.\.\@(\d+)',t)
        if rg:
            start, end = int(rg.group(1)), int(rg.group(2))
            return [float(r[col]) for i,r in enumerate(table) if start <= i <= end]
        else:
            row = int(t[1:])
            if (row < len(table)):
                return float(table[row][col] or 0 )
    return 'invalid reference (%s, %s)' % (t, col)

def rpn(v,col=0, env=[],table=[]):
    global user_ops,log
    s=[]
    if v.startswith(':'):
        user_fn = v.strip(';').split()
        user_ops[user_fn[1]] = user_fn[2:]
        return ''
    words=v.split()
    try:
        while words:
            word = words[0]
            words = words[1:]
            log.write(word + str(s)+'\n')
            if word and set(word).issubset(set("0123456789.-")):
                s.append(float(word))
            elif word in user_ops:
                words = user_ops[word] + words
            elif word.startswith('$') or word.startswith('@'):
                s.append(ref(word,col,env,table))
            elif word in stack:
                stack[word](s)
            else:
                s.append(ops(word,s))
            log.write('after'+word + str(s)+" user fun" + str(user_ops)+'\n')
    except Exception as e:
        return 'err: %s %s %s'%(str(s),str(e), str(s))
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
