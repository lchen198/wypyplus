"""Optional Forth calculator and spreadsheet tables for WyPyPlus.

Put this file next to wypyplus.py to turn it on; delete it to turn it off.
wypyplus.py imports it only if it exists, and adds the rules in R below to
its formatting rules. Nothing else in wypyplus.py changes.

  RPN(3 4 + 2 *)        on a page shows 14
  |=$1 $2 +             in a {| ... |} table is a spreadsheet formula

Security: this is a closed language. Every word is in one of the tables
below or defined by the page with ': name ... ;'. Nothing ever looks up or
calls Python attributes, so a page cannot reach the rest of the program.
All arithmetic is done on floats, so a page cannot build gigantic integers
or strings, and every evaluation stops after 10,000 steps.
"""
import html
import math
import re

q = html.escape

D = {}   # Words defined with ': name ... ;'. Cleared each time a page is formatted.

# Words that take two values: a b op -> result.
B = {'+': lambda a, b: float(a) + float(b),
     '-': lambda a, b: float(a) - float(b),
     '*': lambda a, b: float(a) * float(b),
     '/': lambda a, b: float(a) / float(b),
     '^': lambda a, b: float(a) ** float(b),
     '>': lambda a, b: float(a > b),           # Comparisons give 1.0 or 0.0.
     '<': lambda a, b: float(a < b),
     '=': lambda a, b: float(a == b)}

# Words that take one value. sum and avg take a range from a table.
U = {'sqrt': math.sqrt, 'abs': abs, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
     'log': math.log, 'int': math.floor, 'sum': sum, 'avg': lambda v: sum(v) / len(v)}

# Stack words.
K = {'dup': lambda S: S.append(S[-1]),                   # a -> a a
     'drop': lambda S: S.pop(),                          # a ->
     'swap': lambda S: S.extend([S.pop(), S.pop()]),     # a b -> b a
     'over': lambda S: S.append(S[-2]),                  # a b -> a b a
     'rot': lambda S: S.append(S.pop(-3))}               # a b c -> b c a


def num(v):
    """'3' or '2.5' -> a float; anything else is returned unchanged."""
    return float(v) if re.fullmatch(r'-?\d+\.?\d*', v) else v


def fmt(v):
    """Show floats with up to 12 significant digits (2.0 -> '2')."""
    return '%.12g' % v if isinstance(v, float) else str(v)


def E(m):
    """Stop evaluation with an error message."""
    raise ValueError(m)


def ref(t, r, c, V):
    """A table cell reference, inside a formula in row r, column c.

    $3       column 3 of this row          @2      row 2 of this column
    @2$3     row 2, column 3               $1..$4  columns 1-4 of this row (a list)
    @1..@3   rows 1-3 of this column (a list)
    Rows and columns count from 0. A bad reference raises an error.
    """
    m = re.fullmatch(r'([@$])(\d+)(?:\$(\d+)|\.\.[@$](\d+))?', t)
    a = int(m[2])
    if m[3]:
        return V[a][int(m[3])]
    if m[4]:
        return V[r][a:int(m[4]) + 1] if m[1] == '$' else [V[k][c] for k in range(a, int(m[4]) + 1)]
    return V[r][a] if m[1] == '$' else V[a][c]


def run(T, S, C, O, W, N, r, c, V):
    """Run the words T.

    S is the stack, C the if/else state (one True/False per open 'if'), O the
    printed output, W a ': name ... ;' definition being collected, N the step
    counter, and r, c, V the table cell and values (V is None outside tables).
    """
    for t in T:
        N[0] += 1
        if not N[0] < 1e4:
            E('too long')
        if W and t == ';':                    # End of a definition.
            D[W[1]] = W[2:]
            W.clear()
        elif W or t == ':':                   # Start of, or inside, a definition.
            W.append(t)
        elif t == 'if':                       # Run what follows only if the top value is true.
            C.append(all(C) and bool(S.pop()))
        elif t == 'else':
            C[-1] = all(C[:-1]) and not C[-1]
        elif t == 'then':
            C.pop()
        elif not all(C):                      # Inside a branch that is not taken.
            pass
        elif t in D:                          # A word defined on the page.
            run(D[t], S, C, O, W, N, r, c, V)
        elif t in B:
            S.append(B[t](S.pop(-2), S.pop()))
        elif t in U:
            S.append(U[t](S.pop()))
        elif t in K:
            K[t](S)
        elif t == '.':                        # Print the top value.
            O.append(fmt(S.pop()))
        elif t[0] == '"':                     # "a string"
            S.append(t[1:-1])
        elif t[0] in '$@' and V:              # A cell reference (tables only).
            S.append(ref(t, r, c, V))
        elif (v := num(t)) != t:              # A number.
            S.append(v)
        else:
            E('unknown word ' + t)


def rpn(s, r=0, c=0, V=None, F=0):
    """Evaluate the Forth source s (HTML-escaped page text).

    Returns the printed output, or else the stack, as escaped HTML. With F set
    (table formulas) returns the raw top value instead. Any error gives
    'Err: ...' (or 'Err' in a table) instead of breaking the page.
    """
    try:
        S, O = [], []
        run(re.findall(r'"[^"]*"|\S+', html.unescape(s)), S, [], O, [], [0], r, c, V)
        return S[-1] if F else q(' '.join(O) if O else ' '.join(map(fmt, S)))
    except Exception as e:
        return 'Err' if F else 'Err: ' + q(str(e))


def tb(m):
    """MediaWiki-style table:  {| ... |}  that can also be a spreadsheet.

    Rows are separated by '|-'. Cells start with '|' or are separated by '||'.
    The text after '{|' (a table title) is ignored. A cell starting with '='
    is a formula, e.g. '=$1 $2 +'. Formulas are evaluated three times over, so
    a formula can use the result of a formula further down or to the right.
    Plain cells are shown exactly as written (already HTML-escaped by fs());
    formula results are escaped here.
    """
    R = [[c.strip() for c in re.split(r'\|{1,2}', r)[1:]] for r in re.split(r'\|-', m.group(2))]
    V = [[num(html.unescape(c)) for c in w] for w in R]       # Cell values for references.
    for _ in '123':
        for a, w in enumerate(R):
            for b, c in enumerate(w):
                if c[:1] == '=':
                    V[a][b] = rpn(c[1:], a, b, V, 1)
    return '<table>' + '\n'.join(
        '<tr><td>' + '</td><td>'.join(q(fmt(V[a][b])) if c[:1] == '=' else c for b, c in enumerate(w)) + '</td></tr>'
        for a, w in enumerate(R)) + '</table>'


# The rules wypyplus.py adds to its own, right after {{NAME}}. Like all its
# rules, they see page text that is already HTML-escaped, line by line.
R = (
    (r'\A', lambda m: D.clear() or ''),               # Forget defined words on every new page.
    (r'RPN\((.*?)\)', lambda m: rpn(m.group(1))),     # RPN(2 3 +) -> 5
    (r'(?:\{\|(.*)\n)(.*[^\}]+)(\|\})', tb),          # {| ... |} tables, with =formulas.
)
