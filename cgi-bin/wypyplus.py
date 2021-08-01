#!/usr/bin/env python2
# -*- coding: utf-8 -*- 
import sys,re,os,cgi,rpn;from datetime import timedelta as td,datetime as dt;
home='WyPyPlus';edit='✎'
pre='(?:^|\n)```((?:.|\n)+?)\n```';pre_h='<pre><code>((?:.|\n)+?)</code></pre>';t='</textarea>'
remove_leading_space=lambda m:'<pre><code>'+'\n'.join([l[1:] for l in m.group(1).splitlines()])+'</code></pre>'
insert_leading_space=lambda m: '\n```'+'\n '.join(m.group(1).splitlines())+ '\n```'
q,x,h,w=cgi.escape,os.path.exists,'<a href=','wypyplus.py?p=';
link='\[([^]]*)]\(\s*((?:http[s]?://)?[^)]+)\s*\)';yt="https://www.youtube.com/watch?v="
hl=lambda m,n:'<h%d>%s</h%d>'%(n,m.group(1),n);hl1=lambda m:hl(m, 1);hl2=lambda m:hl(m, 2);hl3=lambda m:hl(m,3)
load=lambda n:(x('w/'+n) and open('w/'+n).read()) or '';
load_tpl=lambda n: load(n) or load('Tpl'+n[:3]) or '';load_g=lambda:load('GlobalMenu')
def load_rec(f):return [load_rec(l[8:l.find(')')]) if l.startswith('INCLUDE(') else l for l in load(f).splitlines()]
f,i=cgi.FormContent(),'put type';
y=f.get('p',[''])[0];y=dt.now().strftime("%b%d") if y=='Today' else (home,y)[y.isalnum()]
se='<form><input type="text"placeholder="Search.. "name="p"><input type="hidden" name="q" value="f"><button type="submit">Search</button></form>'
fs=lambda s:re.sub(pre_h,remove_leading_space,reduce(lambda s,r:re.sub('(?m)'+r[0],r[1],s),(('\r',''),
('^INCLUDE\((\w+)\)$',lambda m: '\n'.join((lambda l: sum(map(flatten,l),[]) if isinstance(l,list) else [l])(load_rec(m.group(1))))),
('RPN\((.*?)\)', lambda m: rpn.rpn(m.group(1))),('(^|[^=/\-_A-Za-z0-9?])@(\w\w+)',lambda m: h+w+m.group(2)+'&amp;q=f>@'+m.group(2)+'</a>'),
('(\{\|\n)(.*[^\}]+)(\|\})',rpn.rpn_table),('(^|[^=/\-_A-Za-z0-9?])([A-Z][a-z]+([A-Z0-9][a-z0-9]*){1,})',
     lambda m:(m.group(1)+'%s%s')%((m.group(2),h+w+m.group(2)+'&amp;q=e>?</a>' if edit else ''),
                                       ('',h+w+m.group(2)+'>%s</a>'%m.group(2)))[x('w/'+m.group(2))]),
('^\{\{$','\n<ul>'),('^\*(.*)$','<li>\g<1></li>'),('^}}$','</ul>'),('^---$','<hr>'),
(pre,'<pre><code>\g<1></code></pre>'),('^# (.*)$',hl1),('^## (.*)$', hl2),('^### (.*)$',hl3),('\*\*([^\*]+)\*\*','<b>\g<1></b>'),
('\!'+link,'<img src="\g<2>" alt="\g<1>">'),('(^|[^!])'+link,"\g<1>"+h+'"\g<3>">\g<2></a>'),('(^|[^"])(http[s]?:[^<>"\s]+)',
 lambda m: ('<iframe width="560" height="315" src="https://www.youtube.com/embed/%s" frameborder="0" allow="accelerometer; autoplay;\
 clipboard-write; encrypted-media;gyroscope; picture-in-picture" allowfullscreen></iframe>' % m.group(2)[len(yt):]) if m.group(2).startswith(yt)
 else (m.group(1)+h+m.group(2)+">"+m.group(2)+"</a>")),('\n\n','\n<p>')),q(s)),0,re.MULTILINE)
do=lambda m,n:{'get':lambda:'<div class="navbar"><h1>%s%s%s>%s</a>'%(h,w,home,home) + ((':%s%s%s&amp;q=f>%s</a>%s%s%s&amp;q=e>%s</a>'%(h,w,n,n,h,w,n,edit)) if edit else '') +
      '</h1></div><div class="main">%s<p>%s'%(se if edit else '',fs(load_g()+re.sub(pre, insert_leading_space, load_tpl(n))) or n),
    'edit':lambda:'<form name="e" action=%s%s method=POST><h1>%s <in%s=hidden name=p value=%s></h1>\
Opened at: %s AutoSave at: %s<textarea name=t id=ta rows=24>%s%s<in%s=submit>'%(
        w,n,fs(n),i,n, dt.now().strftime("%m/%d/%Y %H:%M"), (dt.now()+td(minutes=30)).strftime("%H:%M"), q(load_tpl(n)),t,i),
    'find':lambda:('<h1>Links: %s</h1>'%fs(n))+fs('\n---\n'.join(
        sorted(filter(lambda x: not x.endswith(':\n\n'),[d if n == "All" or n in d else d+':\n\n'+'\n\n'.join(
            [line for line in load(d).splitlines() if n in line and '@'+n not in line]) for d in os.listdir('w/')]))))}.get(m)()
main=lambda f=f:`(os.getenv("REQUEST_METHOD")!="POST") or not edit or ('t' in f or (os.remove('w/'+y) and False))\
    and open('w/'+y,'w').write(f['t'][0])`+`sys.stdout.write("Content-type: text/html; charset=utf-8\r\n\r\n"\
        '<head><meta content="width=device-width, initial-scale=1" name="viewport"></script><link rel="stylesheet" href="../sakura.css">\
        <link rel="stylesheet" href="../nav.css"><script type="text/javascript" src="../ASCIIMathML.js"></script></head><title>%s</title>'%y+
do(({'e':'edit','f':'find'} if edit else {'f':'find'}).get(f.get('q',[None])[0],'get'),y))`;
(__name__=="__main__") and main()
