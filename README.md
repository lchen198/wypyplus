# 🍦WyPyPlus: A personal wiki in 41 lines of code

🍦WyPyPlus (pronounced "whippy plus") is a minimalist wiki in 41 lines of Python, based on [wypy wiki](http://infomesh.net/2003/wypy/) written by Sean B. Palmer in 2004 during a [ShortestWikiContest](http://wiki.c2.com/?ShortestWikiContest).

WyPyPlus is a journey to discover the essence of personal wiki and get rid of everything else. At the end of the day, don't you want a Wiki that just works?

## Features
* Auto-links WikiWords and supports common markdown syntax. See [DemoPage](w/DemoPage).
* Full-text search and a reverse index (tags) for every page.
* Templates, INCLUDE(WikiName) and a global menu, enough for a [GetThingsDone](w/GetThingsDone) system.
* Stores pages as plain text files in the `w` folder. No database, no config files.
* Read-only mode: set `edit=''` in `wypyplus.py`, then dump a static site with wget.

## Install and Run
You need Python 3 (3.8 or newer). Nothing else.
```
cd wypyplus
python3 wypyplus.py
```
Then open http://127.0.0.1:8000/ in your browser. Press Ctrl-C to stop.

WyPyPlus is a plain [WSGI](https://peps.python.org/pep-3333/) app (`app` in `wypyplus.py`). Running the file starts Python's built-in server on 127.0.0.1, so the wiki is only reachable from your own machine. You can also host it with any WSGI server, e.g. `gunicorn wypyplus:app`.

## Design Tradeoffs
* Only a subset of markdown is supported.
* Tags are matched with regular expressions instead of a real parser. Not perfect, but fairly usable.
* No config file. If you really need something, edit the source code.
