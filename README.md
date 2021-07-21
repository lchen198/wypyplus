# WyPyPlus: A personal wiki in 23 lines of code

WyPyPlus (pronounced "whippy plus") is a minimalist wiki server in 23 lines of code. It is an extension of [wypy wiki](http://infomesh.net/2003/wypy/) written by Sean B. Palmer. The original project implements a wiki in just 11 lines of Python code, which is an amazing achievement. However, wypy wiki doesn't have many features I consider as essential.

![screenshot](example.png)

## New Features:
* Only 23 lines of Python code.
* A modernized and mobile-friendly look using [Sakura CSS](https://github.com/oxalorg/sakura).
* Wiki pages save to plain text files under the "w" directory
* Delete a wiki page from disk by saving an empty content.
* Support common markdown syntax as shown in the [DemoPage](https://github.com/lchen198/wypyplus/blob/main/w/DemoPage).
* Aggregate wiki page by tags.

## Text Formatting
* WikiNames are replaced with internal links.
* Markdown style ****bold****
* "\n{{" starts an unordered list.
* "\n* [text]" is a list item in an unordered list.
* "\n}}" ends an unordered list.
* "\n#" inserts H1
* "\n##" inserts H2
* "\n###" inserts H3
* "\n\`\`\`" inserts \<pre\>\<code\>
* "\n\`\`\'" inserts \<\/code\>\<\/pre\>
* "---" creates an \<hr\> element.
* Markdown style [link](https://www.markdownguide.org/basic-syntax/#links) and [image tag](https://www.markdownguide.org/basic-syntax/#images-1).
* All HTML is replaced with its quoted equivalent (i.e. is forbidden).

## WyPyPlus vs Other Wiki Software

WyPyPlus is the result of a deep meditation and soul searching to find out what do I really need for taking personal notes. 

I tried many solutions in the last decade including MoinMoin wiki, DokuWiki, TiddlyWiki, ZIM，Emacs Org mode and many more. I take work-related notes with Org mode and it works well for me. 

I want to keep control of my personal data. Cloud-based services are not ideal for me. Desktop wiki often have display issues when running across multi platforms and various size of screens.
Setting up a personal wiki server is not easy. I would set up a Linux and secure it, configure a web front-end, and initialize a database. After that I also need to worry about backing up the data and keep the system up-to-date. The more features it has, the higher maintenance cost I need to pay. Things add up pretty quickly. 

### The key feature of WyPyPluse is the lack of features. (AKA Less is More)

It is just slightly better than a Windows notepad. Wiki pages are just text files. If you don't want WyPyPlus, you can easily move to somewhere else.

**Benefits** 
* Fast!!
* Support just enough wiki synataxes to be useful. (See [DemoPage](https://github.com/lchen198/wypyplus/blob/main/w/DemoPage))
* Takes less than one minute to setup.
* Runs anywhere that has Python and a browser.
* Works perfectly offline.
* No config file to mess with.
* No authentication. It's a personal wiki and you should run it on your own machine. 
* No database. Wiki pages are just text files.
* No Javascript.
* Low maintenance. Just backup the entire folder. 
* Extendable.

![demo](example2.png)

## Install and Use

* You need Python 2 to run this applicaiton. Mac and Linux already have python 2. For Windows users, please install Python 2.7.

* Download WyPyPlus and extract it to a folder (E.g wypy_wiki). This folder should already contain a cgi-bin directory and a "w" directory. Your file will save into the "w" directory.

* The following command should work under Mac, Linux and Windows.

```
cd wypy_wiki

python -m CGIHTTPServer 8000 

Open this url in your browser
http://127.0.0.1:8000/cgi-bin/wypyplus.py
```

Since the wypyplus file is just a cgi script, you can also use any web server to host it. 

The UI should be fairly self-explanatory. 
* Click the ? mark after a CamelCased word to create a new page.
* Click the Submit button to save a page. If you save an empty page, WyPyPlus will delete it from disk.

### How to create tags
There's no different between Tags and WikiWords. When you create a new page, there will be a link on the top of the screen to show all pages that reference it. 

For example, you can create a page called MyTag, and put the word MyTag to other pages and see references here:
http://127.0.0.1:8000/cgi-bin/wypyplus?p=MyTag&q=f

# Design Tradeoffs

* To keep things minimum, WyPyPlus only supports a subset of markdown syntaxes. 
* To avoid depending on an external parser, WyPyPlus uses regular expresisons to match tags. It is not perfect, but farily useable.
* WyPyPlus has no config file. You can't mis-config it. If you really need something, just edit the source code.
* WyPyPlus doesn't automatically save for you. Don't refresh the page before submitting your change.

# Source Code

The original wypy code is highly compressed. However, variable names are carefully picked so that the code is still somewhat readable. If you read it through, it is not that hard to change.

For example, if you don't like the CSS, just replace ```<head><link rel='stylesheet' href='https://unpkg.com/sakura.css/css/sakura.css' type='text/css'></head> ```with whatever you like.

To support new syntax, you can add a tuple of (regex_pattern, replace_pattern). The following example extracts content after ## and enclose it with an h2 headline. 
```
('^## (.*)$', '<h2>\g<1></h2>')
```

