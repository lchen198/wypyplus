#!/usr/bin/env python2
# -*- coding: utf-8 -*-
pre='(?:^|\n)```((?:.|\n)+?)\n```';link='\[([^]]*)]\(\s*((?:http[s]?://)?[^)]+)\s*\)';import sys,re,os,cgi;
from datetime import timedelta as td,datetime as dt;q,x,h,w=cgi.escape,os.path.exists,'<a href=','wypyplus.py?p='
load,t=lambda n:(x('w/'+n) and open('w/'+n).read()) or (x('w/'+'Tpl'+n[:3]) and open('w/'+'Tpl'+n[:3]).read()) or '','</textarea>'
f,i=cgi.FormContent(),'put type';y=f.get('p',[''])[0];y=('WyPyPlus',y)[y.isalnum()]
fs,do,main=lambda s:re.sub('^ #', '#',reduce(lambda s,r:re.sub('(?m)'+r[0],r[1],s),(('\r',''),
('(^|[^=/\-_A-Za-z0-9?])([A-Z][a-z]+([A-Z0-9][a-z0-9]*){1,})',
lambda m:(m.group(1)+'%s'+h+w+m.group(2)+'%s>%s</a>')%((m.group(2),'&amp;q=e','?'),('','',m.group(2)))[x('w/'+m.group(2))]),
('^\{\{$','\n<ul>'),('^\* ','<li>'),('^}}$','</ul>'),('^---$','<hr>'),(pre,'<pre>\g<1></pre>'),
('^# (.*)$','<h1>\g<1></h1>'),('^## (.*)$', '<h2>\g<1></h2>'),('^### (.*)$','<h3>\g<1></h3>'),
('\*\*(.*)\*\*','<b>\g<1></b>'),('\!'+link,'<img src="\g<2>" alt="\g<1>">'),('(^|[^!])'+link,"\g<1>"+h+'"\g<3>">\g<2></a>'),('(^|[^"])(http[s]?:[^<>"\s]+)',"\g<1>"+h+'"\g<2>">\g<2></a>'),
('\n\n','<p>')),q(s)),0,re.MULTILINE),lambda m,n:{'get':'<h1>%s%sWyPyPlus>WyPyPlus</a>:%s%s%s&amp;q=f>%s</a>:%s%s%s&amp;q=e>✎</a></h1><form><input type="text" placeholder="Search.." \
name="p"><input type="hidden" name="q" value="f"><button type="submit">Search</button></form><p>%s'%(h,w,h,w,n,n,h,w,n,
fs(re.sub(pre, lambda m: '\n'.join([i if not i.startswith('#') else ' '+i for i in m.group(0).splitlines()]), load(n))) or n),\
'edit':'<form name="e" action=%s%s method=POST><h1>%s <in %s=hidden name=p value=%s><in%s=submit></h1>Opened at: %s AutoSave at: %s<textarea name=t id=ta cols=80 rows=24>%s'\
%(w,n,fs(n),i,n,i,dt.now().strftime("%m/%d/%Y %H:%M"),(dt.now()+td(minutes=30)).strftime("%H:%M"),q(load(n)))+t,\
'find':('<h1>Links: %s</h1>'%fs(n))+fs('{{\n* %s\n}}'%'\n* '.join(sorted([d for d in os.listdir('w/') if n == "All" or load(d).count(n)])))
}.get(m),lambda f=f:`(os.getenv("REQUEST_METHOD")!="POST") or ('t' in f or (os.remove('w/'+y) and False))\
and open('w/'+y,'w').write(f['t'][0])`+`sys.stdout.write("Content-type: text/html; charset=utf-8\r\n\r\n"\
'<head><meta content="width=device-width, initial-scale=1" name="viewport"><link rel="stylesheet" href="../sakura.css"></script>\
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/latest.js?config=AM_CHTML"></script></head><title>%s</title>'%y+do({'e':'edit','f':'find'}.get(f.get('q',[None])[0],'get'),y))`;
(__name__=="__main__") and main()
