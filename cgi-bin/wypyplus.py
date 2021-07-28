#!/usr/bin/env python2
# -*- coding: utf-8 -*-
name='WyPyPlus';edit='✎';pre='(?:^|\n)```((?:.|\n)+?)\n```';pre_h='<pre><code>((?:.|\n)+?)</code></pre>';link='\[([^]]*)]\(\s*((?:http[s]?://)?[^)]+)\s*\)';t='</textarea>'
hs=lambda m:hex(hash(m.group(1)))[-5:];hl=lambda m,n:'<h%d>%s</h%d>'%(n,m.group(1),n);hl1=lambda m:hl(m, 1);hl2=lambda m:hl(m, 2);hl3=lambda m:hl(m,3) 
import sys,re,os,cgi;from datetime import timedelta as td,datetime as dt;q,x,h,w=cgi.escape,os.path.exists,'<a href=','wypyplus.py?p='
load=lambda n:(x('w/'+n) and open('w/'+n).read()) or '';load_tpl=lambda n: load(n) or load('Tpl'+n[:3]) or '';load_g=lambda:load('GlobalMenu')
f,i=cgi.FormContent(),'put type';y=f.get('p',[''])[0];y=dt.now().strftime("%b%d") if y=='Today' else (name,y)[y.isalnum()];se='<form><input type="text"placeholder="Search.. "name="p"><input type="hidden" name="q" value="f"><button type="submit">Search</button></form>'
fs,do,main=lambda s:re.sub(pre_h,lambda m:'<pre><code>'+'\n'.join([l[1:] for l in m.group(1).splitlines()])+'</code></pre>',reduce(lambda s,r:re.sub('(?m)'+r[0],r[1],s),
(('\r',''),('^@INCLUDE=(\w+)$',lambda m: x('w/'+m.group(1)) and open('w/'+m.group(1)).read() or ''),('(^|[^=/\-_A-Za-z0-9?])([A-Z][a-z]+([A-Z0-9][a-z0-9]*){1,})',
lambda m:(m.group(1)+'%s%s')%((m.group(2),h+w+m.group(2)+'&amp;q=e>?</a>' if edit else ''),('',h+w+m.group(2)+'>%s</a>'%m.group(2)))[x('w/'+m.group(2))]),
('^\{\{$','\n<ul>'),('^\*(.*)$','<li>\g<1></li>'),('^}}$','</ul>'),('^---$','<hr>'),(pre,'<pre><code>\g<1></code></pre>'),('^# (.*)$',hl1),
('^## (.*)$', hl2),('^### (.*)$',hl3),('\*\*(.*)\*\*','<b>\g<1></b>'),('\!'+link,'<img src="\g<2>" alt="\g<1>">'),('(^|[^!])'+link,"\g<1>"+h+'"\g<3>">\g<2></a>'),
('(^|[^"])(http[s]?:[^<>"\s]+)',"\g<1>"+h+'"\g<2>">\g<2></a>'),('\n\n','\n<p>')),q(s)),0,re.MULTILINE),\
lambda m,n:{'get':'<h1>%s%s%s>%s</a>:%s%s%s&amp;q=f>%s</a>%s%s%s&amp;q=e>%s</a></h1>%s<p>%s'%(h,w,name,name,h,w,n,n,h,w,n,edit,se if edit else '',
fs(load_g()+re.sub(pre, lambda m: '\n```'+'\n '.join(m.group(1).splitlines())+ '\n```', load_tpl(n))) or n),\
'edit':'<form name="e" action=%s%s method=POST><h1>%s <in%s=hidden name=p value=%s></h1>Opened at: %s AutoSave at: %s<textarea name=t id=ta rows=24>%s%s<in%s=submit>'\
%(w,n,fs(n),i,n,dt.now().strftime("%m/%d/%Y %H:%M"),(dt.now()+td(minutes=30)).strftime("%H:%M"),q(load_tpl(n)),t,i),\
'find':('<h1>Links: %s</h1>'%fs(n))+fs('{{\n* %s\n}}'%'\n* '.join(sorted([d for d in os.listdir('w/') if n == "All" or load(d).count(n) or n in d])))
}.get(m),lambda f=f:`(os.getenv("REQUEST_METHOD")!="POST") or not edit or ('t' in f or (os.remove('w/'+y) and False))\
and open('w/'+y,'w').write(f['t'][0])`+`sys.stdout.write("Content-type: text/html; charset=utf-8\r\n\r\n"\
'<head><meta content="width=device-width, initial-scale=1" name="viewport"><link rel="stylesheet" href="../sakura.css">\
</head><title>%s</title>'%y+do(({'e':'edit','f':'find'} if edit else {'f':'find'}).get(f.get('q',[None])[0],'get'),y))`;(__name__=="__main__") and main()
