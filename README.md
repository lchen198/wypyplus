# WyPyPlus: A personal wiki in 23 lines of code

WyPyPlus (pronounced "whippy plus") is a minimalist wiki server in 23 lines of code based on [wypy wiki](http://infomesh.net/2003/wypy/) written by Sean B. Palmer in 2004 during a [ShortestWikiContest](http://wiki.c2.com/?ShortestWikiContest).

WyPyPlus is a journey to discover the essence of personal wiki and get rid of everything else. It tries to keep a minimal set of features and pack them in the tiniest space possible.

It tries to be an old typewriter with the magic of linking information. There’s nothing between you and your content. You don’t need to worry about configuration, backup, user authentication, subscription fee, system update and so on. It is just you and your content. At the end of the day, don't you want a Wiki that just works and is free?

Other software projects always tell you that they are easy to set up and easy to use. WyPyPlus tells you that it is easy for you to leave. Your content are text files stored under the /w directory. You can move to other places if you need more than what WyPyPlus offers.

Visit a **static site** [Demo](https://ctrl-c.club/~lchen/cgi-bin/wypyplus.py%3Fp=WyPyPlus.html). WyPyPlus has a read-only mode. When combined with [wget](https://www.gnu.org/software/wget/), you can create a static site.

<p align="center">
<img src="example.png"> 
</p>
A minimal editor that does not get in the way.
<p align="center">
<img src="editor.png">
</p>
The Built-in Calendar 
<p align="center"><img src="calendar.png"></p>

### You will be amazed by how much you can do with a simple tool.

* Only 23 lines of Python code with no external dependency other than the standard library. (2.6KB Python + 3.9KB CSS)
* Runs on Mac, Linux and Windows.
* Support basic wiki syntax. [DemoPage](https://github.com/lchen198/wypyplus/blob/main/w/DemoPage)
* Your files are in the /w folder.

### To make your life easier
* An example calendar and daily journal.
* An example GetThingsDone guide to help you set up GTD quickly.
* A [template](#how-to-define-and-use-a-template) system to insert pre-defined content.
* Full-text search.
* A modernized and mobile-friendly look using [Sakura CSS](https://github.com/oxalorg/sakura).
* Delete a wiki page from disk by saving an empty content.
* Each WikiPage has a reverse index. You can use this feature to group pages by tags.
* An [index page](http://127.0.0.1:8000/cgi-bin/wypyplus.py?p=All&q=f) to show all your files in sorted order.
* AutoSave after 30 minutes of editing.
* Use @INCLUDE=WikiPage to include content from another page.
* (Optional) Syntax highlight with [highlight.js](https://highlightjs.org).
* (Optional) Display [AsciiMath](http://asciimath.org) or LaTaX notations.
* (Optional) Display headline anchor links.
* (Optional) Read-only mode. You can use it to [generate a static site](#how-to-use-the-read-only-mode). 
* (Optional) Automatically include the "GlobalMenu" page if it exists.
* Fully commented [source code](https://github.com/lchen198/wypyplus/blob/main/cgi-bin/wypyplus_with_comment.py).

<p align="center">
<img src="example2.png">
</p>

**Other Benefits** 
* Fast!!
* Takes less than a minute to set up and get going.
* Works perfectly offline.
* No config file to mess with.
* No authentication. It's a personal wiki and you should run it on your own machine. 
* No database. Wiki pages are just text files.
* Low maintenance. Just backup the entire folder. 

**Design Tradeoffs**

* To keep things minimal, WyPyPlus only supports a subset of markdown syntaxes. 
* To avoid depending on an external parser, WyPyPlus uses regular expression to match tags. It is not perfect, but fairly useable. 
* WyPyPlus has no config file. You can't mis-configure it. If you really need something, just edit the source code.

## Text Formatting
* WikiNames are replaced with internal links.
* Markdown style ```**bold**```
* "\n{{" starts an unordered list.
* "\n* [text]" is a list item in an unordered list.
* "\n}}" ends an unordered list.
* "\n#" inserts H1
* "\n##" inserts H2
* "\n###" inserts H3
* To format code or text into its own distinct block, use triple backticks: \`\`\`.
* "---" creates an \<hr\> element.
* Markdown style [link](https://www.markdownguide.org/basic-syntax/#links) and [image tag](https://www.markdownguide.org/basic-syntax/#images-1).
* "\n@INCLUDE=WikiPage" to include the content from another page. 
* All HTML is replaced with its quoted equivalent (i.e. is forbidden).

## Install and Use

* You need Python 2 to run this application. Mac and most Linux distro already have Python 2. For Windows users, please install [Python 2.7](https://www.python.org/download/releases/2.7/).

* Download WyPyPlus and extract it to a folder (E.g wypy_wiki).
```
cd wypy_wiki

# Fpr Python 2. Note that the page is exposed in both 127.0.0.1 
# and your local network IP (usually 192.168.x.x). You can use this script to add password authentication.
# https://github.com/lchen198/wypyplus/wiki#how-to-add-password-authentication-in-python-2
python -m CGIHTTPServer 8000 

# For Python 3, you can bind it just to your localhost.
python3 -m http.server --cgi 8000 --bind 127.0.0.1

Open this url in your browser. It takes a few moments to start.
http://127.0.0.1:8000/cgi-bin/wypyplus.py
```

### How to use the read-only mode

If you use Linux or Mac, you can use the [gen_site.sh](https://github.com/lchen198/wypyplus/blob/main/gen_static.sh) script to pack the site automatically.

**Otherwise, you can do it manually with the following steps:**

You need to modify the **edit** variable in wypyplus.py. It holds the icon of the edit button. Set it to an empty string and WyPyPlus will run in read-only mode.

In read-only mode, WyPyPlus

* Will not generate the edit link.
* Will not generate links for WikiWords when they don't exist.
* Will not handle the POST method, which means that your data is read-only.
* Will hide the search bar.

If you want to go a step further, you can generate a static site using wget. The following command dumps the entire site as html pages.
```
wget \
     --recursive \
     --page-requisites \
     --html-extension \
     --convert-linksl\
     --no-parent \
         http://127.0.0.1:8000/cgi-bin/wypyplus.py
```

After that, you can create an index.html with the following content to redirect the index page to cgi-bin/wypyplus.py.html.

```
<meta http-equiv="Refresh" content="0; url='cgi-bin/wypyplus.py.html'" />
```



### How to create tags
Tags are just wiki pages. When you create a new page, there will be a link on the top of the screen to show all pages that reference it. 

For example, you can create a page called ToDo, and put the word ToDo to other pages and see references here:
http://127.0.0.1:8000/cgi-bin/wypyplus?p=ToDo&q=f

### How to define and use a template
You can create a template just like any other wiki page. A template name must start with "Tpl" and follow by three characters. WyPyPlus will automatically insert its content to a new wiki page when the first three characters of the page matches the template

For example, If you create a template page called TplJan, a new page called Jan23 will load the content from the template. 

# How do I customize WyPyPlus?

A fully commented source code is available here:
[wypyplus_with_comment.py](https://github.com/lchen198/wypyplus/blob/main/cgi-bin/wypyplus_with_comment.py)

You can easily modify the souce code.  If you don't like the CSS, just replace ```<head><link rel='stylesheet' href='..\sakura.css' type='text/css'></head> ```with whatever you like. You can find a lot more themes in [this site](https://dohliam.github.io/dropin-minimal-css).

If you want to add support for AsciiMath or LaTeX, include the following:
```
 <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

To support new syntax, you can add a tuple of (regex_pattern, replace_pattern). The following example extracts content after ## and enclose it with an h2 headline: 
```
('^## (.*)$', '<h2>\g<1></h2>')
```

Another example to change color for certain text:
```
('TODO','<b style="color:red;">\g<0></b>'),('DONE','<b style="color:green;">\g<0></b>'),
```
