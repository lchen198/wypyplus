#!/usr/bin/env python3
"""WyPyPlus, formatted and commented.

This file behaves exactly like wypyplus.py. It exists so people can read and
audit the code; run either one. Names match the 42-line version (load, fs, do,
app, ...) so each part can be compared side by side.

How a request flows:
  1. app() parses the form fields, works out which page was asked for, and
     saves or deletes the page on a POST.
  2. do() builds the HTML for one of three views: show a page, edit a page,
     or find (search / back-links).
  3. fs() turns wiki text into HTML: escape everything first, then apply a
     list of regular-expression rules in order.

Pages are plain text files in the w/ folder. There are no other files,
no database and no JavaScript.
"""
import html
import os
import re
import threading
from datetime import datetime as dt
from functools import reduce
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs
from wsgiref.simple_server import WSGIServer, make_server

# Run from the script's own folder, so 'w/' and 'sakura.css' are found no
# matter where the server was started from.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

home = 'WyPyPlus'   # Page shown when no (valid) page name is given.
edit = '✎'          # Edit-link icon. Set to '' for read-only mode: no edit
                    # links, no saving, no search box.
i = 'put type'      # Used to spell '<input type' as '<in' + i (saves bytes).
L = threading.Lock()  # One request renders at a time (see app()).

# Code blocks: ``` on its own line, the code, then ``` again.
pre = '(?:^|\n)```((?:.|\n)+?)\n```'
# The same block after it has been turned into HTML.
pre_h = '<pre><code>((?:.|\n)+?)</code></pre>'
t = '</textarea>'


def insert_leading_space(m):
    """Indent every line inside a code block by one space.

    The formatting rules below are anchored at the start of a line ('# ',
    '* ', 'INCLUDE(' ...). A leading space keeps them from firing on code.
    """
    return '\n```' + '\n '.join(m.group(1).splitlines()) + '\n```'


def remove_leading_space(m):
    """Undo insert_leading_space() once the page has been converted."""
    return '<pre><code>' + '\n'.join([l[1:] for l in m.group(1).splitlines()]) + '</code></pre>'


q = html.escape       # Escapes & < > " and ' in page text (security: no HTML
                      # from pages ever reaches the browser unescaped).
x = os.path.exists
h = '<a href='        # Start of a link.
w = 'wypyplus.py?p='  # Link to a page. The app ignores the URL path, so these
                      # links work whichever file name is running.

# Markdown link or image: [text](url) / ![alt](url).
# Security: the URL must start with http:// or https://, or have no scheme at
# all (a relative link). Anything with a scheme before the first / ? or #
# (javascript:, data:, ...) does not match and stays as plain text.
link = r'\[([^]]*)]\(\s*((?:https?://|(?![^/?#)]*:))[^)]+)\s*\)'
yt = "https://www.youtube.com/watch?v="   # These links become embedded videos.


def hl(m, n):
    """Heading of level n."""
    return '<h%d>%s</h%d>' % (n, m.group(1), n)


def hl1(m): return hl(m, 1)
def hl2(m): return hl(m, 2)
def hl3(m): return hl(m, 3)


def load(n):
    """Return the text of page n, or '' if there is no such page.

    Security: only names made of letters and digits are read, so no name can
    point outside the w/ folder (no '/', '.', '..').
    """
    return (n.isalnum() and x('w/' + n) and open('w/' + n, encoding='utf-8').read()) or ''


def load_tpl(n):
    """Page n, or for a new page its template: 'Tpl' + the first 3 letters.

    Example: a new page Jan23 starts with the text of TplJan.
    """
    return load(n) or load('Tpl' + n[:3]) or ''


def load_g():
    """The GlobalMenu page, shown at the top of every page."""
    return load('GlobalMenu')


def flatten(l):
    """Turn nested lists into one flat list."""
    return sum(map(flatten, l), []) if isinstance(l, list) else [l]


def load_rec(f, s=()):
    """Lines of page f, with INCLUDE(Name) lines replaced by that page.

    s is the chain of pages already being included. A page that is already in
    the chain is not included again, so a page that includes itself (directly
    or through others) cannot recurse forever; its INCLUDE line stays as text.
    """
    s += (f,)
    return [load_rec(n, s) if l.startswith('INCLUDE(') and (n := l[8:l.find(')')]) not in s else l
            for l in load(f).splitlines()]


# The search box. It sends ?p=<words>&q=f, the find view.
se = ('<form><input type="text"placeholder="Search.. "name="p"><input type="hidden" '
      'name="q" value="f"><button type="submit">Search</button></form>')


def table(m):
    """MediaWiki-style table:  {| ... |}

    Rows are separated by '|-'. Cells start with '|' or are separated by '||'.
    The text after '{|' (a table title) is ignored. Cell text was already
    HTML-escaped by fs().
    """
    rows = re.split(r'\|-', m.group(2))
    return '<table>' + '\n'.join(
        '<tr><td>' + '</td><td>'.join(c.strip() for c in re.split(r'\|{1,2}', r)[1:]) + '</td></tr>'
        for r in rows) + '</table>'


def wiki_word(m):
    """WikiWord -> link to that page.

    If the page does not exist yet, show the word plus a '?' link to create
    it (or just the word in read-only mode).
    """
    before, word = m.group(1), m.group(2)
    if x('w/' + word):
        return before + h + w + word + '>%s</a>' % word
    return before + word + (h + w + word + '&amp;q=e>?</a>' if edit else '')


def raw_url(m):
    """A bare http(s) URL in the text: YouTube links become an embedded
    video, everything else a plain link."""
    before, url = m.group(1), m.group(2)
    if url.startswith(yt):
        return ('<iframe width="560" height="315" src="https://www.youtube.com/embed/%s" frameborder="0" allow="accelerometer; autoplay;'
                ' clipboard-write; encrypted-media;gyroscope; picture-in-picture" allowfullscreen></iframe>' % url[len(yt):])
    return before + h + url + ">" + url + "</a>"


def fs(s, y):
    """Format wiki text s as HTML. y is the current page name.

    Security: the text is HTML-escaped FIRST (q(s)), so a page can never
    contain raw HTML. The rules below only add tags of their own. Each rule
    is (regex, replacement) and they run in this order, line by line
    (re.MULTILINE: ^ and $ match at every line).
    """
    rules = (
        ('\r', ''),                                          # Windows line endings.
        (r'^INCLUDE\((\w+)\)$',                              # INCLUDE(Page) on its own line.
         lambda m: '\n'.join(flatten(load_rec(m.group(1))))),
        (r'\{\{NAME\}\}', y),                                # {{NAME}} -> current page name.
        (r'(^|[^=/\-_A-Za-z0-9?])@([A-Z]\w+)',               # @Tag -> find every page mentioning it.
         lambda m: h + w + m.group(2) + '&amp;q=f>@' + m.group(2) + '</a>'),
        (r'(?:\{\|(.*)\n)(.*[^\}]+)(\|\})', table),          # {| ... |} tables.
        (r'(^|[^=/\-_A-Za-z0-9?])([A-Z][a-z]+([A-Z0-9][a-z0-9]*){1,})',  # WikiWords.
         wiki_word),
        (r'^\{\{$', '\n<ul>'),                               # {{ starts a list,
        (r'^\*(.*)$', r'<li>\g<1></li>'),                    # * is a list item,
        ('^}}$', '</ul>'),                                   # }} ends the list.
        ('^---$', '<hr>'),                                   # Horizontal line.
        (pre, r'<pre><code>\g<1></code></pre>'),             # ``` code blocks.
        ('^# (.*)$', hl1),                                   # Headings.
        ('^## (.*)$', hl2),
        ('^### (.*)$', hl3),
        (r'\*\*([^\*]+)\*\*', r'<b>\g<1></b>'),              # **bold**
        (r'\!' + link, r'<img src="\g<2>" alt="\g<1>">'),    # ![alt](url) images.
        ('(^|[^!])' + link, r"\g<1>" + h + r'"\g<3>">\g<2></a>'),  # [text](url) links.
        # Bare URLs. Skipped right after a quote: either one this function
        # wrote (src="..., href="...) or an escaped one from the text (&quot;).
        (r'(^|[^";])(https?:(?:(?!&quot;)[^<>"\s])+)', raw_url),
        ('\n\n', '\n<p>'),                                   # Blank line -> new paragraph.
    )
    s = reduce(lambda s, r: re.sub('(?m)' + r[0], r[1], s), rules, q(s))
    return re.sub(pre_h, remove_leading_space, s, flags=re.M)


def do(m, n):
    """Build the HTML for view m ('get', 'edit' or 'find') of page n."""
    if m == 'get':
        # Title bar: home link, then the page name (a link to its back-links)
        # and the edit icon, then the search box and the page itself.
        bar = '<div class="navbar"><h1>%s%s%s>%s</a>' % (h, w, home, home)
        if edit:
            bar += ':%s%s%s&amp;q=f>%s</a>%s%s%s&amp;q=e>%s</a>' % (h, w, n, n, h, w, n, edit)
        body = fs(load_g() + re.sub(pre, insert_leading_space, load_tpl(n)), n)
        return bar + '</h1></div><div class="main">%s<p>%s' % (se if edit else '', body or n)

    if m == 'edit':
        # A plain form. The textarea holds the escaped page text (or the
        # template, for a new page), so '</textarea>' in a page cannot close it.
        return ('<form name="e" action=%s%s method=POST><h1>%s <in%s=hidden name=p value=%s></h1>'
                '<textarea name=t id=ta rows=24>%s%s<in%s=submit>' % (w, n, fs(n, n), i, n, q(load_tpl(n)), t, i))

    if m == 'find':
        # Search and back-links. "All" lists every page. Otherwise list pages
        # whose name contains n, plus every page with lines that mention n,
        # showing those lines (lines that are just the '@n' tag are left out).
        found = []
        for d in os.listdir('w/'):
            if n == "All" or n.lower() in d.lower():
                found.append(d)
            else:
                lines = [line for line in load(d).splitlines() if n.lower() in line.lower() and '@' + n not in line]
                found.append(d + ':\n\n' + '\n\n'.join(lines))
        found = sorted(filter(lambda x: not x.endswith(':\n\n'), found))   # Drop pages with no match.
        return ('<h1>Links: %s</h1>' % fs(n, n)) + fs('\n---\n'.join(found), n)


def app(e, r):
    """The WSGI application: one call per HTTP request.

    e is the request environment, r starts the response.
    """
    # Only one request is handled at a time, so two saves can never mix up
    # pages or write the same file at once. Rendering is fast, so this is fine
    # for a personal wiki. The server still runs each connection in its own
    # thread, so an idle browser connection cannot block everyone else.
    with L:
        s = e['PATH_INFO'][1:]
        # The only static file served. No other path can read a file.
        if s == 'sakura.css':
            r('200 OK', [('Content-Type', 'text/css')])
            return [open(s, 'rb').read()]

        # Form fields from the POST body and the URL, e.g. p=Page&q=e.
        # parse_qs drops empty values, so saving an empty page sends no 't'.
        body = e['wsgi.input'].read(int(e.get('CONTENT_LENGTH') or 0)).decode() if e['REQUEST_METHOD'] == 'POST' else ''
        f = parse_qs(body + '&' + e.get('QUERY_STRING', ''))

        # The page name. 'Today' becomes e.g. 'Oct2'. Security: anything that
        # is not only letters and digits falls back to the home page, so a
        # name can never be a path.
        y = f.get('p', [''])[0]
        y = dt.now().strftime("%b") + str(dt.now().day) if y == 'Today' else (home, y)[y.isalnum()]

        # Save (or delete, when the text is empty). Security: only when editing
        # is on, and never for a form posted from another website (CSRF).
        # Browsers send Sec-Fetch-Site; tools like curl send nothing ('none').
        if e['REQUEST_METHOD'] == 'POST' and edit and e.get('HTTP_SEC_FETCH_SITE', 'none') in ('same-origin', 'none'):
            if 't' in f:
                open('w/' + y, 'w', encoding='utf-8', newline='').write(f['t'][0])
            elif x('w/' + y):
                os.remove('w/' + y)

        # Pick the view: ?q=e edit, ?q=f find, anything else shows the page.
        # In read-only mode only 'find' is allowed.
        views = {'e': 'edit', 'f': 'find'} if edit else {'f': 'find'}
        view = views.get(f.get('q', [None])[0], 'get')

        # Security: the CSP header stops every script (the wiki has none) and
        # stops other sites from showing the wiki in a frame (clickjacking).
        r('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
                     ('Content-Security-Policy', "script-src 'none'; frame-ancestors 'none'")])
        return [('<head><meta content="width=device-width, initial-scale=1" name="viewport">'
                 '<link rel="stylesheet" href="sakura.css"></head><title>%s</title>' % y
                 + do(view, y)).encode()]


class Server(ThreadingMixIn, WSGIServer):
    """Python's built-in WSGI server, one thread per connection.

    Without threads, browsers that open spare connections (Chrome, Edge)
    would leave the single-threaded server waiting, and no page would load.
    """
    daemon_threads = True   # Ctrl-C does not wait for open connections.


if __name__ == "__main__":
    # Listens on 127.0.0.1 only: reachable from this machine, not the network.
    # To share it, put a server with a password in front (see README.md).
    print('http://127.0.0.1:8000', flush=True)
    make_server('127.0.0.1', 8000, app, Server).serve_forever()
