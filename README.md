# 🍦WyPyPlus: A personal wiki in 42 lines of code

🍦WyPyPlus (pronounced "whippy plus") is a minimalist wiki server in 42 lines of code based on [wypy wiki](http://infomesh.net/2003/wypy/) written by Sean B. Palmer in 2004 during a [ShortestWikiContest](http://wiki.c2.com/?ShortestWikiContest).

WyPyPlus is a journey to discover the essence of personal wiki and get rid of everything else. It tries to keep a minimal set of features and pack them in the tiniest space possible. At the end of the day, don't you want a Wiki that just works?


## Some Use Cases

### A Personal Wiki
*  WyPyPlus supports auto-link on WikiWords and common markdown syntaxes. It also creates a reverse index for every page and supports full-text search.

### An Outliner Focusing on Content Creation
*  WyPyPlus allows you to break down a large topic to small pages. You can focus on one thing at a time. After you finish, you can merge everything together using the @INCLUDE=PageName syntax. This is inspired by the hot-list feature in [GrandView](https://welcometosherwood.wordpress.com/2009/10/10/grandview/), which I considered as one of the best outliner of all time.

### A [GetThingsDone](https://en.wikipedia.org/wiki/Getting_Things_Done) System
* WyPyPlus comes with a calendar and detailed instructions on setting up a complete GTD system. It also supports page templates and contextual tags. 

### A Static Site Generator:
*  When you run WyPyPlus in read-only mode, you can dump the entire site using wget. Visit the [(Demo)](https://ctrl-c.club/~lchen/cgi-bin/wypyplus.py%3Fp=WyPyPlus.html) site to see for yourself.
 
### A Presentation Tool:
* You can use WyPyPlus to create presentations and produce [PDFs](https://github.com/lchen198/wypyplus/blob/main/example_hardcopy.pdf)!

## Some Screenshots
![](example.png)
![](editor.png)
![](calendar.png)
![](example2.png)

# Core Features
* Takes less than a minute to set up.
* Only 42 lines of code with no external dependency except Python.
* Runs on Mac, Linux and Windows.
* Supports basic wiki syntax. [DemoPage](https://github.com/lchen198/wypyplus/blob/main/w/DemoPage)
* Stores wiki pages as plain text files. 
* Works perfectly offline.
* No config files to mess with.
* No database to backup up.

# Design Tradeoffs

* To keep things minimal, WyPyPlus only supports a subset of markdown syntaxes. 
* To avoid depending on an external parser, WyPyPlus uses regular expressions to match tags. It is not perfect, but fairly usable. 
* WyPyPlus has no config file. You can't mis-configure it. If you really need something, just edit the source code.


## Install and Run in 2 Minutes.

* You need Python 2 to run this application. For Windows users, please install [Python 2.7](https://www.python.org/download/releases/2.7/).

* Put WyPyPlus to a folder (E.g wypy_wiki).
```
cd wypy_wiki

# For Python 2
python -m CGIHTTPServer 8000 

# For Python 3
python3 -m http.server --cgi 8000 --bind 127.0.0.1

Open either URL in your browser:

http://127.0.0.1:8000/
Or 
http://127.0.0.1:8000/cgi-bin/wypyplus.py
```
Note that Python2 exposes your page to your local network. You can add a password with this [launcher](https://github.com/lchen198/wypyplus/wiki#how-to-add-password-authentication-in-python-2)
