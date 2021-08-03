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
    'format': lambda s, out: str.format(s.pop(), s.pop())
    }

two={'+':op.add,'-':op.sub,'*':op.mul,'/':op.div,'^':pow, 'randint':random.randint}
ops=lambda t,s: unary_op(unary[t],s) if t in unary \
  else two_op(two[t],s) if t in two \
  else 'undefined function:' + t
user_ops = {}
log=open('./log','w')
CELL_NUM, CELL_STR, CELL_FUN, CELL_CONTINUE = 0, 1, 2, 4
ERROR, OK, DEFER = 0, 1, 2

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
    crt_row = table[row]
    rval = None
    if t.startswith('$'):
        rg = re.match('\$(\d+)\.\.\$(\d+)',t)
        if rg:
            start, end = int(rg.group(1)), int(rg.group(2))
            rval = [v for v in crt_row[start:end+1]]
        else:
            if int(t[1:]) < len(crt_row):
                rval = crt_row[int(t[1:])]
    elif t.startswith('@'):
        rg = re.match('\@(\d+)\.\.\@(\d+)',t)
        row_col=re.match('\@(\d+)\$(\d+)',t)
        if rg:
            start, end = int(rg.group(1)), int(rg.group(2))
            rval = [r[col] for i,r in enumerate(table) if start <= i <= end]
        elif row_col:
            t_row, t_col = int(row_col.group(1)), int(row_col.group(2))
            log.write('ref r c'+ str(t_row) + " " + str(t_col)+'\n')
            if t_row < len(table) and t_col < len(table[t_row]):
                    rval = table[t_row][t_col]
        else:
            target_row = int(t[1:])
            if (target_row < len(table)):
                rval = table[target_row][col]
    if not rval:
        return 'invalid reference (%s, @%s, $%s)' % (t, row, col), ERROR
    if has_defer_ref(rval):
        return t, DEFER
    else:
        return rval, OK

def tokenize(v):
    STR, NUM, FUN, SP = 1, 2, 3,4
    state = SP
    t = []
    toks = []
    for i, c in enumerate(v+' '):
        if state == SP:
            if c in ['"',"'"]:
                state = STR
            elif c == " ":
                continue
            elif c in set("0123456789") or (c in ['.', '-'] and i+1 < len(v) and v[i+1] in set("0123456789")):
                state = NUM
            else:
                state = FUN
        if state == NUM:
            if c == ' ':
                if t:
                    try: num = float(''.join(t))
                    except:
                        num=''.join(t)
                    toks.append(num)
                    t = []
                    state = SP
            else:
                t.append(c)
        if state == FUN:
            if c == ' ':
                if t:
                    toks.append(''.join(t))
                    t = []
                    state = SP
            else:
                t.append(c)              
        if state == STR:
          t.append(c)
          if len(t) > 1 and c == t[0]:
              toks.append(''.join(t))
              t = []
              state = SP
    return toks

# def convert(v):
#     try:
#         value = int(v)
#         return CELL_NUM, value
#     except:
#         try:
#             value = float(v)
#             return CELL_NUM, value
#         except:
#             return CELL_STR, v
    
def rpn_str(v, row=0, col=0,table=[]):
    global user_ops
    if v.startswith(':'):
        user_fn = v.strip(';').split()
        user_ops[user_fn[1]] = user_fn[2:]
        return ''
    words=tokenize(v)
    rval, status = rpn(words, [], [],row, col,table)
    if status in [OK, ERROR]:
        return str(rval)
    else:
        return ''


def rpn(words,s,output, row=0, col=0,table=[]):
    global user_ops, log
    log.write('rpn:'+str(s)+str(words)+str(row)+str(col)+'\n')
    while words:
        word = words[0]
        words = words[1:]
        log.write('rpn:'+str(word)+str(s)+str(words)+str(row)+str(col)+'\n')
        if type(word) == int or type(word) == float:
            s.append(word)
        elif word.startswith('"') or word.startswith("'"):
            s.append(word.strip('"\''))
        elif word in user_ops:
            words = user_ops[word] + words
        elif word.startswith('$') or word.startswith('@'):
            ref_data,status = ref(word,row,col,table)
            if status == DEFER:
                continuation = lambda r,c,t:rpn([word]+words[:],s[:],output[:],r,c,t)
                return (continuation, DEFER)
            if status == ERROR:
                return ref_data, ERROR
            if type(ref_data) == list:
                s.append([cell[1] for cell in ref_data])
            else:
                s.append(ref_data[1])
        elif word in misc_fn:
            rval = misc_fn[word](s,output)
            if rval:
                s.append(rval)
        else:
            s.append(ops(word,s))
    if output:
        return ''.join([str(o) for o in output]), OK
    else:
        log.write("rpn finish"+str(s) +'\n')
        return s[0] if len(s)==1 else str(s), OK

def rpn_table(m):
    table_env=[]
    table = []
    max_iter = 3
    table_status = OK
    log.write(m.group(2))

    for row_i, row in enumerate(re.split('\|-',m.group(2))):
        table_env.append([])
        row_env = table_env[-1]
        for col_i, v in enumerate(map(str.strip,re.split('\|{1,2}',row)[1:])):
            log.write(str(col_i) + " "+str(v)+'\n')
            if v.startswith('='):
                log.write(str(tokenize(v[1:]))+'\n')
                def init(r,c,t,words=tokenize(v[1:])):
                    return rpn(words,[],[], r,c,t)
                
                row_env.append((CELL_FUN, init))
            else:
                try:
                    value = float(v)
                    row_env.append((CELL_STR, value))
                    continue
                except:
                    pass
                value = v
                row_env.append((CELL_STR, value))

    try:
        for cur_iter in range(max_iter):
            row_status = []
            for row_i, row in enumerate(table_env):
                for col_i, cell in enumerate(row):
                    cell_type, cell_val = cell
                    log.write('cell (%d %d) %d %s\n' %(row_i, col_i, cell_type, str(cell_val)))
                    if cell_type == CELL_FUN:
                        cell_rval, status = cell_val(row_i, col_i,table_env)
                        log.write('fun %s %s\n' %(status, cell_rval))
                        row_status.append(status)
                        if status == DEFER:
                            table_env[row_i][col_i] = (CELL_FUN, cell_rval)
                        else:
                            if type(cell_rval) == str:
                                table_env[row_i][col_i] = (CELL_STR, cell_rval)
                            else:
                                table_env[row_i][col_i] = (CELL_NUM, cell_rval)
                        if status == ERROR:
                            table_env[row_i][col_i] = (CELL_STR, cell_rval)
                    else:
                        pass
            if any([s == DEFER for s in row_status]):
                continue
    except:
        pass
    for row_env in table_env:
        table.append('<tr><td>'+'</td><td>'.join([str(v) for cell_type,v in row_env])+'</td></tr>')
    return '<table>'+'\n'.join(table)+'</table>'
            
            
if __name__ == "__main__":
    import doctest
    doctest.testmod()        
