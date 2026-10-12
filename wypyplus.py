#!/usr/bin/env python3
import re, os, html, threading; from functools import reduce; from urllib.parse import parse_qs; from datetime import datetime as dt
from socketserver import ThreadingMixIn; from wsgiref.simple_server import make_server, WSGIServer; os.chdir(os.path.dirname(os.path.abspath(__file__)))
home, edit, i, L = 'WyPyPlus', '✎', 'put type', threading.Lock()                                                                                      # home page, edit icon ('' = read-only), '<in'+i, one request at a time
q, x, h, w       = html.escape, os.path.exists, '<a href=', 'wypyplus.py?p='                                                                          # escape, file exists, link start, page link
pre, pre_h, t    = '(?:^|\n)```((?:.|\n)+?)\n```', '<pre><code>((?:.|\n)+?)</code></pre>', '</textarea>'                                              # ``` code blocks, before and after
link, yt         = r'\[([^]]*)]\(\s*((?:https?://|(?![^/?#)]*:))[^)]+)\s*\)', 'https://www.youtube.com/watch?v='                                      # [text](url): http(s) or relative only
X                = __import__('forth').R if x('forth.py') else ()                                                                                     # optional add-on rules from forth.py
se               = '<form><input type="text"placeholder="Search.. "name="p"><input type="hidden" name="q" value="f"><button type="submit">Search</button></form>'
load     = lambda n: (n.isalnum() and x('w/' + n) and open('w/' + n, encoding='utf-8').read()) or ''                                                  # letters and digits only: never outside w/
load_tpl = lambda n: load(n) or load('Tpl' + n[:3]) or '';   load_g = lambda: load('GlobalMenu');   flatten = lambda l: sum(map(flatten, l), []) if isinstance(l, list) else [l]
def load_rec(f, s=()): s += (f,); return [load_rec(n, s) if l.startswith('INCLUDE(') and (n := l[8:l.find(')')]) not in s else l for l in load(f).splitlines()]  # no loops
insert_leading_space = lambda m: '\n```' + '\n '.join(m.group(1).splitlines()) + '\n```';   remove_leading_space = lambda m: '<pre><code>' + '\n'.join([l[1:] for l in m.group(1).splitlines()]) + '</code></pre>'
table = lambda m: '<table>' + '\n'.join('<tr><td>' + '</td><td>'.join(c.strip() for c in re.split(r'\|{1,2}', r)[1:]) + '</td></tr>' for r in re.split(r'\|-', m.group(2))) + '</table>'
word  = lambda m: (m.group(1) + '%s%s') % ((m.group(2), h + w + m.group(2) + '&amp;q=e>?</a>' if edit else ''), ('', h + w + m.group(2) + '>%s</a>' % m.group(2)))[x('w/' + m.group(2))]
url   = lambda m: ('<iframe width="560" height="315" src="https://www.youtube.com/embed/%s" frameborder="0" allow="accelerometer; autoplay; clipboard-write; '
                   'encrypted-media;gyroscope; picture-in-picture" allowfullscreen></iframe>' % m.group(2)[len(yt):]) if m.group(2).startswith(yt) else (m.group(1) + h + m.group(2) + '>' + m.group(2) + '</a>')
RULES = (('\r', ''),  (r'^INCLUDE\((\w+)\)$', lambda m: '\n'.join(flatten(load_rec(m.group(1))))),  (r'\{\{NAME\}\}', lambda m: y),  *X,              # line ends, INCLUDE, {{NAME}}, add-ons
         (r'(^|[^=/\-_A-Za-z0-9?])@([A-Z]\w+)',                          h + w + r'\g<2>&amp;q=f>@\g<2></a>'),                                        # @Tag
         (r'(?:\{\|(.*)\n)(.*[^\}]+)(\|\})',                              table),                                                                     # {| tables |}
         (r'(^|[^=/\-_A-Za-z0-9?])([A-Z][a-z]+([A-Z0-9][a-z0-9]*){1,})',  word),                                                                      # WikiWords
         (r'^\{\{$', '\n<ul>'),  (r'^\*(.*)$', r'<li>\g<1></li>'),  ('^}}$', '</ul>'),  ('^---$', '<hr>'),                                            # {{ lists }}, ---
         (pre, r'<pre><code>\g<1></code></pre>'),  ('^# (.*)$', r'<h1>\g<1></h1>'),  ('^## (.*)$', r'<h2>\g<1></h2>'),  ('^### (.*)$', r'<h3>\g<1></h3>'),  # code, headings
         (r'\*\*([^\*]+)\*\*', r'<b>\g<1></b>'),  (r'\!' + link, r'<img src="\g<2>" alt="\g<1>">'),  ('(^|[^!])' + link, r'\g<1>' + h + r'"\g<3>">\g<2></a>'),  # bold, images, links
         (r'(^|[^";])(https?:(?:(?!&quot;)[^<>"\s])+)',                  url),  ('\n\n', '\n<p>'))                                                    # bare URLs, paragraphs
fs = lambda s: re.sub(pre_h, remove_leading_space, reduce(lambda s, r: re.sub('(?m)' + r[0], r[1], s), RULES, q(s)), flags=re.M)                      # escape everything, then apply RULES
do = lambda m, n: {'get':  lambda: '<div class="navbar"><h1>%s%s%s>%s</a>' % (h, w, home, home) + ((':%s%s%s&amp;q=f>%s</a>%s%s%s&amp;q=e>%s</a>' % (h, w, n, n, h, w, n, edit)) if edit else '')
                                   + '</h1></div><div class="main">%s<p>%s' % (se if edit else '', fs(load_g() + re.sub(pre, insert_leading_space, load_tpl(n))) or n),
                   'edit': lambda: '<form name="e" action=%s%s method=POST><h1>%s <in%s=hidden name=p value=%s></h1><textarea name=t id=ta rows=24>%s%s<in%s=submit>' % (w, n, fs(n), i, n, q(load_tpl(n)), t, i),
                   'find': lambda: ('<h1>Links: %s</h1>' % fs(n)) + fs('\n---\n'.join(sorted(filter(lambda x: not x.endswith(':\n\n'), [d if n == "All" or n.lower() in d.lower()
                                   else d + ':\n\n' + '\n\n'.join([line for line in load(d).splitlines() if n.lower() in line.lower() and '@' + n not in line]) for d in os.listdir('w/')]))))}.get(m)()
def app(e, r):
  with L:
    global f, y; s = e['PATH_INFO'][1:]
    if s == 'sakura.css': r('200 OK', [('Content-Type', 'text/css')]); return [open(s, 'rb').read()]                                                  # the only static file
    f = parse_qs((e['wsgi.input'].read(int(e.get('CONTENT_LENGTH') or 0)).decode() if e['REQUEST_METHOD'] == 'POST' else '') + '&' + e.get('QUERY_STRING', ''))  # form + URL
    y = f.get('p', [''])[0]; y = dt.now().strftime('%b') + str(dt.now().day) if y == 'Today' else (home, y)[y.isalnum()]                              # page name: letters/digits only
    if e['REQUEST_METHOD'] == 'POST' and edit and e.get('HTTP_SEC_FETCH_SITE', 'none') in ('same-origin', 'none'):                                    # save, but never from another site
      open('w/' + y, 'w', encoding='utf-8', newline='').write(f['t'][0]) if 't' in f else x('w/' + y) and os.remove('w/' + y)                         # empty text deletes the page
    r('200 OK', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Security-Policy', "script-src 'none'; frame-ancestors 'none'")])             # no scripts, no framing
    return [('<head><meta content="width=device-width, initial-scale=1" name="viewport"><link rel="stylesheet" href="sakura.css"></head><title>%s</title>' % y + do(({'e': 'edit', 'f': 'find'} if edit else {'f': 'find'}).get(f.get('q', [None])[0], 'get'), y)).encode()]
if __name__ == '__main__': print('http://127.0.0.1:8000', flush=True); make_server('127.0.0.1', 8000, app, type('S', (ThreadingMixIn, WSGIServer), {'daemon_threads': True})).serve_forever()
