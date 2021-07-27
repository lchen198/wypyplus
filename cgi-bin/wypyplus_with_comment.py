#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys,re,os,cgi;from datetime import timedelta as td,datetime as dt;
edit='✎' # The edit button. Set it to an empty string to turn on read-only mode.
# Match the <pre></pre> tag before and after the expansion. Since the
# code uses regex to match tag, it doesn't know if a ^# is a comment
# or is a headline. Therefore, the solution is to insert a space at
# the beginning of every line inside the pre tags and remove them
# later.
pre='(?:^|\n)```((?:.|\n)+?)\n```';pre_h='<pre><code>((?:.|\n)+?)</code></pre>'

# Match wiki link [text](url)
link='\[([^]]*)]\(\s*((?:http[s]?://)?[^)]+)\s*\)'

# Hash function to generate headline id.
hs=lambda m:hex(hash(m.group(1)))[-5:]
# Functions to convert headline 1 to 3
hl=lambda m,n:'<h%d>%s</h%d>'%(n,m.group(1),n);hl1=lambda m:hl(m, 1);hl2=lambda m:hl(m, 2);hl3=lambda m:hl(m,3)
q=cgi.escape
x=os.path.exists
h='<a href='
w='wypyplus_with_comment.py?p='
# Load content from w/ if the file does not exist, try to load from a template.
load=lambda n:(x('w/'+n) and open('w/'+n).read()) or (x('w/'+'Tpl'+n[:3]) and open('w/'+'Tpl'+n[:3]).read()) or ''
t='</textarea>'
f=cgi.FormContent()
# shortcut for input tag. Use together with <in%s='submit'> % i
i='put type'
# Get requested page name. Convert 'Today' to Month+Day.
y=f.get('p',[''])[0];y=dt.now().strftime("%b%d") if y=='Today' else ('WyPyPlus',y)[y.isalnum()]

# Handle wiki syntax. Remove the inserted space at the beginning of each line inside <pre></pre>. 
fs=lambda s:re.sub(pre_h,lambda m:'<pre><code>'+'\n'.join([l[1:] for l in m.group(1).splitlines()])+'</code></pre>',
reduce(lambda s,r:re.sub('(?m)'+r[0],r[1],s), (('\r',''),
('^@INCLUDE=(\w+)$',lambda m: x('w/'+m.group(1)) and open('w/'+m.group(1)).read() or ''), # Inline files
# Match WikiWord and convert it to a link. If the file doesn't exist, add a ? mark at the end.
('(^|[^=/\-_A-Za-z0-9?])([A-Z][a-z]+([A-Z0-9][a-z0-9]*){1,})', lambda m:(m.group(1)+'%s'+h+w+m.group(2)+'%s>%s</a>')%(
    (m.group(2),'&amp;q=e','?'),('','',m.group(2)))[x('w/'+m.group(2))]),
('^\{\{$','\n<ul>'),('^\*(.*)$','<li>\g<1></li>'),('^}}$','</ul>'),
('^---$','<hr>'),
(pre,'<pre><code>\g<1></code></pre>'),
('^# (.*)$',hl1),('^## (.*)$', hl2),('^### (.*)$',hl3),
('\*\*(.*)\*\*','<b>\g<1></b>'),
('\!'+link,'<img src="\g<2>" alt="\g<1>">'),('(^|[^!])'+link,"\g<1>"+h+'"\g<3>">\g<2></a>'),
('(^|[^"])(http[s]?:[^<>"\s]+)',"\g<1>"+h+'"\g<2>">\g<2></a>'),('\n\n','\n<p>')),q(s)),0,re.MULTILINE)

# Handle get, edit and find.
do=lambda m,n:{
    # Load content, generate a page and insert an extra space at the beginning of each line inside <pre></pre>.
    'get':'<h1>%s%sWyPyPlus>WyPyPlus</a>:%s%s%s&amp;q=f>%s</a>%s%s%s&amp;q=e>%s</a>\
</h1><form><input type="text" placeholder="Search.." name="p"><input type="hidden" name="q" value="f">\
<button type="submit">Search</button></form><p>%s'%(
        h,w,h,w,n,n,h,w,n,edit,
        fs(re.sub(pre, lambda m: '\n```'+'\n '.join(m.group(1).splitlines())+ '\n```', load(n))) or n),
    # Load content, create a form. 
    'edit':'<form name="e" action=%s%s method=POST><h1>%s <in%s=hidden name=p value=%s>\
</h1>Opened at: %s AutoSave at: %s<textarea name=t id=ta rows=24>%s%s<in%s=submit>'\
%(w,n,fs(n),i,n,dt.
      # Compute open time and auto save time.
      now().strftime("%m/%d/%Y %H:%M"),
      (dt.now()+td(minutes=30)).strftime("%H:%M"),
      q(load(n)),t,i),
    # Search for a keyword in wiki pages or in file names
    'find':('<h1>Links: %s</h1>'%fs(n))+fs('{{\n* %s\n}}'%'\n* '.join(
        sorted([d for d in os.listdir('w/') if n == "All" or load(d).count(n) or n in d])))
}.get(m)

# Handle post method.If the content is empty, delete the file. Otherwise, write it to disk.
main=lambda f=f:`(os.getenv("REQUEST_METHOD")!="POST") or\
  not edit or('t' in f or (os.remove('w/'+y) and False)) and open('w/'+y,'w').write(f['t'][0])\
  `+`\
  sys.stdout.write(
      'Content-type: text/html; charset=utf-8\r\n\r\n<head><meta content="width=device-width, initial-scale=1" name="viewport">\
<link rel="stylesheet" href="../sakura.css"></head><title>%s</title>'%y+\
do(({'e':'edit','f':'find'} if edit else {'f':'find'}).get(
    f.get('q',[None])[0],'get'),y)
      )`;
# Start main
(__name__=="__main__") and main()
