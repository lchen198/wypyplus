import traceback
import sys,contextlib
from io import BytesIO as StringIO
import HTMLParser
parser = HTMLParser.HTMLParser()

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
    m = m.replace('\t', '    ')
    with stdoutIO() as s:
        try:
            exec(parser.unescape(m).lstrip('\n'), globals())
        except Exception as e:
            f = StringIO()
            return "Error:%s\n\n"%('<br>'.join(traceback.format_exc().splitlines()))
    if 'export' in globals():
        if export == 'both':
            return quote(m) + '\n\n' + s.getvalue()
        elif export == 'code':
            return quote(m)
    return s.getvalue()
