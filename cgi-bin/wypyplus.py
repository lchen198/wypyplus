#!/usr/bin/python
# -*- coding: utf-8 -*-
link='\[([^]]*)]\(\s*((?:http[s]?://)?[^)]+)\s*\)';import sys,re,os,cgi;
q,x,h,w=cgi.escape,os.path.exists,'<a href=','wypyplus.py?p='
load,t=lambda n:(x('w/'+n) and open('w/'+n).read()) or '','</textarea></form>'
f,i=cgi.FormContent(),'put type';y=f.get('p',[''])[0];y=('WyPyPlus',y)[y.isalpha()]
fs,do,main=lambda s:reduce(lambda s,r:re.sub('(?m)'+r[0],r[1],s),(('\r',''),(\
'(^|[^=/\-_A-Za-z0-9?])(([A-Z][a-z]+){2,})',lambda m:(m.group(1)+'%s'+h+w+m.group(2)+\
'%s>%s</a>')%((m.group(2),'&amp;q=e','?'),('','',m.group(2)))[x('w/'+m.group(2))]),\
('^\{\{$','\n<ul>'),('^\* ','<li>'),('^}}$','</ul>'),('^---$','<hr>'),('```((?:.|\n)+?)```','<pre>\g<1></pre>'),
('^# (.*)$','<h1>\g<1></h1>'),('^## (.*)$', '<h2>\g<1></h2>'),
('^### (.*)$', '<h3>\g<1></h3>'),('\*\*(.*)\*\*','<b>\g<1></b>'),
('\!'+link,'<img src="\g<2>" alt="\g<1>">'),('(^|[^!])'+link,"\g<1>"+h+'"\g<3>">\g<2></a>'),
('(^|[^"])(http[s]?:[^<>"\s]+)',"\g<1>"+h+'"\g<2>">\g<2></a>'),('\n\n','<p>')),q(s)),\
lambda m,n:{'get':'<h1>%s%s>WyPyPlus</a>:%s%s%s&amp;q=f>%s</a>:%s%s%s&amp;q=e>✎</a></h1><p>%s'%(\
h,w,h,w,n,n,h,w,n,fs(load(n)) or n),'edit':'<form action=%s%s method=POST><h1>%s <in'\
'%s=hidden name=p value=%s><in%s=submit></h1><textarea name=t cols=80 rows=24'\
'>%s'%(w,n,fs(n),i,n,i,q(load(n)))+t,'find':('<h1>Links: %s</h1>'%fs(n))+fs(
'{{\n* %s\n}}'%'\n* '.join([d for d in os.listdir('w/') if n == "All" or load(d).count(n)]))
}.get(m),lambda f=f:`(os.getenv("REQUEST_METHOD")!="POST") or ('t' in f or (os.remove('w/'+y) and False))\
and open('w/'+y,'w').write(f['t'][0])`+`sys.stdout.write("Content-type: text/html; charset=utf-8"\
"\r\n\r\n<head><link rel='stylesheet' href='../sakura.css' type='text/css'>\
</head><title>%s</title>"%y+do({'e':'edit','f':'find'}.get(f.get('q',[None])[0],'get'),y))`;(__name__=="__main__") and main()

