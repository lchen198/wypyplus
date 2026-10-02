# 🍦 WyPyPlus

A personal wiki in one Python file. 42 lines. No dependencies.

Pages are plain text files in the `w` folder. No database, no config, no build step.

## Quick start

You need Python 3.8 or newer.

```
git clone https://github.com/lchen198/wypyplus
cd wypyplus
python3 wypyplus.py
```

Open http://127.0.0.1:8000 and start writing. Press Ctrl-C to stop.

## Writing pages

| You type | You get |
| --- | --- |
| `WikiWord` | A link to that page. Click the `?` to create it. |
| `# Title`, `## Title`, `### Title` | Headings |
| `**bold**` | **bold** |
| `[text](https://example.com)` | A link |
| `![alt](https://example.com/a.png)` | An image |
| `---` | A horizontal line |
| ```` ``` ```` on its own line, before and after | A code block |
| `{{`, then `* item` lines, then `}}` | A bulleted list |
| `@Tag` | A link to every page that mentions `@Tag` |
| `INCLUDE(PageName)` on its own line | The content of another page |
| A YouTube link | An embedded video |

More examples are in the [DemoPage](w/DemoPage).

## Good to know

* **Delete a page:** save it with no text.
* **Templates:** a page named `Tpl` plus three letters (e.g. `TplJan`) is the starting text for new pages that begin with those letters (e.g. `Jan23`).
* **Today:** `?p=Today` opens a page named after today's date, such as `Oct2`.
* **Menu:** text in a page named `GlobalMenu` appears on every page.
* **See all pages:** search for `All`.
* **Read-only mode:** in `wypyplus.py`, change `'✎'` to `''`. Editing, saving and search are turned off.

## Hosting

`wypyplus.py` is a standard [WSGI](https://peps.python.org/pep-3333/) app. Running it directly uses Python's built-in server, which only listens on your own machine. To serve it with something else, point any WSGI server at `wypyplus:app`, for example `gunicorn wypyplus:app`.

There is no login. Anyone who can reach the server can edit pages, so don't expose it to the internet without putting authentication in front of it.

## Credits

Based on [wypy](http://infomesh.net/2003/wypy/), an 11-line wiki written by Sean B. Palmer for the [ShortestWikiContest](http://wiki.c2.com/?ShortestWikiContest). Styled with [Sakura CSS](https://github.com/oxalorg/sakura).

## License

MIT. See [LICENSE](LICENSE).
