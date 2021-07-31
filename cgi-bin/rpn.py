import operator as op;import math,re
unary_op=lambda t,s: t(s.pop())
norm_op=lambda t,s: t(s.pop(-2),s.pop())
rev_op=lambda t,s: t(s.pop(),s.pop())
unary={'sqrt':math.sqrt, 'fabs':math.fabs, 'sin':math.sin, 'cos':math.cos,'tan':math.tan, 'sum':sum, 'avg': lambda v: sum(v)/len(v)}
norm={'+':op.add,'-':op.sub,'*':op.mul,'/':op.div,'^':pow}
rev={'log':math.log};
ops=lambda t,s: unary_op(unary[t],s) if t in unary else norm_op(norm[t],s) if t in norm else rev_op(rev[t],s) if t in rev else 'err'

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
    s=[]
    try:
        for t in v.split():
            if set(t).issubset(set("0123456789.-")):
                s.append(float(t)) 
            elif t.startswith('$') or t.startswith('@'):
                s.append(ref(t,col,env,table))
            else:
                s.append(ops(t,s))
    except Exception as e:
        return 'err: %s %s'%(str(s),str(e))
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
