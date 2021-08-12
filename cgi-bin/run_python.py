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
    
def run_python(m):
    with stdoutIO() as s:
        try:
            exec(parser.unescape(m), globals())
        except Exception as e:
            return str(e)
    return s.getvalue()
