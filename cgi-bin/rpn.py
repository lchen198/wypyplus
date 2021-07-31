import operator as op;import math,re
unary_op=lambda t,s: getattr(math,t)(s.pop());norm_op=lambda t,s: t(s.pop(-2),s.pop());rev_op=lambda t,s: t(s.pop(),s.pop())
unary=['sqrt','fabs','sin','cos','tan'];norm={'+':op.add,'-':op.sub,'*':op.mul,'/':op.div,'^':pow};rev={'log':math.log};
ops=lambda t,s: unary_op(t,s) if t in unary else norm_op(norm[t],s) if t in norm else rev_op(rev[t],s) if t in rev else 'err'
def rpn(v,env=[]):
    try:
        s=[];[s.append(float(t)) if set(t).issubset(set("0123456789.-")) else s.append(float(env[int(t[1:])] or 0 )) if t.startswith('$') else s.append(ops(t,s)) for t in v.split()];return str(s[0]) if len(s)==1 else str(s)
    except: return 'err'
def rpn_row(m):env=[];[env.append(str(v) if not v.startswith('=') else rpn(v[1:],env)) for v in map(str.strip,re.split('\|{1,2}',m)[1:])];return '<tr><td>'+'</td><td>'.join(env)+'</td></tr>'
