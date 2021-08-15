import traceback
import sys,contextlib
from io import BytesIO as StringIO
import HTMLParser
parser = HTMLParser.HTMLParser()

PageDefault = {'include_title': True,
               'hide_nav_bar': False}

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

def quote(s):
    content = '\n'.join([' '+l for l in s.splitlines()])
    return '\n```\n'+content+'\n```\n'

def run_python(m):
    ldict = {}
    m = m.replace('\t', '    ')
    with stdoutIO() as s:
        try:
            exec(parser.unescape(m).lstrip('\n'), globals(), ldict)
        except Exception as e:
            f = StringIO()
            return "Error:%s\n\n"%('<br>'.join(traceback.format_exc().splitlines()))
    if 'export' in ldict:
        export = ldict['export']
        if export == 'both':
            return quote(m) + '\n\n' + s.getvalue()
        elif export == 'code':
            return quote(m)
    return s.getvalue()
