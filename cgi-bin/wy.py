#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# This is a single-file version that doesn't support Forth.
# It uses github style table syntax.
import sys, re, os, cgi, contextlib
from datetime import timedelta as td, datetime as dt
from io import BytesIO as StringIO
home = 'WyPy'
head = '''<head><meta content="width=device-width, initial-scale=1" name="viewport"><link rel="stylesheet" href="../sakura.css"></head>
<script src="../sorttable.js"></script>'''
edit = ' (edit)'
pre = '(?:^|\n)```((?:.|\n)+?)\n```'
pre_h = '<pre><code>((?:.|\n)+?)</code></pre>'
t = '</textarea>'
remove_leading_space = lambda m: '<pre><code>' + '\n'.join(
    [l[1:] for l in m.group(1).splitlines()]) + '</code></pre>'
insert_leading_space = lambda m: '\n```' + '\n '.join(m.group(1).splitlines()
                                                      ) + '\n```'
q, x, h, w = cgi.escape, os.path.exists, '<a href=', 'wy.py?p='
link = '\[([^]]*)]\(\s*((?:http[s]?://)?[^)]+)\s*\)'
yt = "https://www.youtube.com/watch?v="
hl = lambda m, n: '<h%d>%s</h%d>' % (n, m.group(1), n)
hl1 = lambda m: hl(m, 1)
hl2 = lambda m: hl(m, 2)
hl3 = lambda m: hl(m, 3)
load = lambda n: (x('w/' + n) and open('w/' + n).read()) or ''
load_tpl = lambda n: load(n) or load('Tpl' + n[:3]) or ''
load_g = lambda: load('GlobalMenu')
flatten = lambda l: sum(map(flatten, l), []) if isinstance(l, list) else [l]
def load_rec(f):
    return [
        load_rec(l[8:l.find(')')]) if l.startswith('INCLUDE(') else l
        for l in load(f).splitlines()
    ]

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old
    
def run_python(m):
    with stdoutIO() as s:
        try:
            exec(m.group(1), globals())
        except Exception as e:
            return str(e)
    return s.getvalue()
            
f = cgi.FormContent()
y = f.get('p', [''])[0]
today = dt.now().strftime("%b%d")
today = today if today[3] != '0' else today[:3] + today[4]
y = today if y == 'Today' else (home, y)[y != '']
se = '<form><input type="text"placeholder="Search.. "name="p"><input \
type="hidden" name="q" value="f"><button type="submit">Search</button></form>'
fs = lambda s: re.sub(
    pre_h, remove_leading_space,
    reduce(lambda s, r: re.sub('(?m)' + r[0], r[1], s), (
        ('\r', ''), ('\{\{NAME\}\}', y), ('(?:^|\n)PYTHON((?:.|\n)+?)\nPYTHON', run_python),
        ('^INCLUDE\((\w+)\)$', lambda m: '\n'.join(
            flatten(load_rec(m.group(1))))), 
        ('(^|[^=/\-_A-Za-z0-9?])@([A-Z][\w\+\-]+)', lambda m: m.group(1) + h + w + m.group(2) +
         '&amp;q=f>@' + m.group(2) + '</a>'),
        ('(^|[^=/\-_A-Za-z0-9?])([A-Z][a-z]+([A-Z0-9][a-z0-9]*){1,})', lambda
         m: (m.group(1) + '%s%s') %
         ((m.group(2), h + w + m.group(2) + '&amp;q=e>?</a>'
           if edit else ''), ('', h + w + m.group(2) + '>%s</a>' % m.group(2))
          )[x('w/' + m.group(2))]), ('^\{\{$', '\n<ul>'),
        ('^\*(.*)$', '<li>\g<1></li>'), ('^}}$', '</ul>'), ('^---$', '<hr>'),
        (pre, '<pre><code>\g<1></code></pre>'), ('^# (.*)$', hl1),
        ('^(\|[^\n]+\|\r?\n)((?:\|:?[-]+:?)+\|)(\n(?:\|[^\n]+\|\r?\n?)*)?$',
         lambda m: '<table class="sortable"><tr><th>' + '</th><th>'.join(
             m.group(1).strip('|\n').split('|')) + '\n'.join([
                 '<tr><td>' + '</td><td>'.join(line.strip('|\n').split('|')) +
                 '</td></tr>' for line in m.group(3).strip('\n').splitlines()
             ]) + '</table>'), ('^## (.*)$', hl2), ('^### (.*)$', hl3),
        ('\*\*([^\*]+)\*\*', '<b>\g<1></b>'), 
        ('\!' + link, '<img src="\g<2>" alt="\g<1>">'),
        ('(^|[^!])' + link, "\g<1>" + h + '"\g<3>">\g<2></a>'),
        ('(^|[^"])(http[s]?:[^<>"\s]+)', lambda m:
         ('<iframe width="560" height="315" src="https://www.youtube.com/embed\
/%s" frameborder="0" allow="accelerometer; autoplay;clipboard-write; \
encrypted-media;gyroscope; picture-in-picture" allowfullscreen></iframe>' % m.
          group(2)[len(yt):]) if m.group(2).startswith(yt) else
         (m.group(1) + h + m.group(2) + ">" + m.group(2) + "</a>")),
        ('\n\n', '\n<p>')), q(s)), 0, re.MULTILINE)

def search(kw, doc):
    d = load(doc)
    d_lower = d.lower()
    terms = kw.lower().replace('+', ' ').split(' ')
    if not all([d_lower.count(t)>0 for t in terms]):
        return ''
    matches = [ "   "+ line for line in d.splitlines()
                if any([term in line.lower() for term in terms])]
    if matches: 
        return '\n\n'.join(matches)
    return ''
    
do = lambda m, n: {
    'get':
    lambda: '<div class="navbar"><h1>%s%s%s>%s</a>' % (h, w, home, home) + (
        (':%s%s%s&amp;q=f>%s</a>%s%s%s&amp;q=e>%s</a>' %
         (h, w, n, n, h, w, n, edit))
        if edit else '') + '</h1></div><div class="main">%s<p>%s' %
    (se if edit else '',
     fs(load_g() + re.sub(pre, insert_leading_space, load_tpl(n))) or n),
    'edit':
    lambda:
    '<form name="e" action=%s%s method=POST><h1>%s <input type=hidden name=p value=%s></h1>\
<div id="editor"><textarea class="CodeMirror" name=t id=ta cols=80 rows=24>%s%s</div><p><input type=submit>'
    % (w, n, fs(n), n, q(load_tpl(n)), t),
    'find':
    lambda:
    ('<h1>%s%s%s>%s</a>: Search %s</h1><p>%s' %
     (h, w, home, home, fs(n), se if edit else '')) + fs('\n---\n'.join(map(lambda x: x[1],
         sorted(
             filter(lambda x: not x[1].endswith(':\n\n'),
                    [(os.path.getmtime('w/'+d),
                      "### " + d if n == "All" or n.lower() in d.lower(
                      ) else "### " + d + ':\n\n' + search(n, d))
                     for d in os.listdir('w/')]),
             reverse = True))))
}.get(m)()
main=lambda f=f:`(os.getenv("REQUEST_METHOD")!="POST") or not edit or ('t' in f or (os.remove('w/'+y) and False))\
    and open('w/'+y,'w').write(f['t'][0])`+`sys.stdout.write("Content-type: text/html; charset=utf-8\r\n\r\n" + head +
        '<title>%s</title><body>'%y+\
 do(({'e':'edit','f':'find'} if edit else {'f':'find'}).get(f.get('q',[None])[0],'get'),y))`
(__name__ == "__main__") and main()
