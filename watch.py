#!/usr/bin/env python3
"""Fetch each source page in plans.json, strip to text, diff vs last snapshot.
Usage: python3 watch.py   (exit code 1 if any page changed)"""
import json,re,hashlib,difflib,urllib.request,pathlib,html,sys
D=pathlib.Path(__file__).parent; S=D/'snapshots'; S.mkdir(exist_ok=True)
urls=sorted({u.strip() for p in json.load(open(D/'plans.json'))['plans'] for u in p['source'].split(';')})
def text(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 LimitWatch'})
    h=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore')
    h=re.sub(r'(?is)<(script|style|noscript).*?</\1>',' ',h); t=html.unescape(re.sub(r'<[^>]+>','\n',h))
    return '\n'.join(l.strip() for l in t.splitlines() if l.strip())
changed=0
for u in urls:
    f=S/(hashlib.sha1(u.encode()).hexdigest()[:12]+'.txt')
    try: new=text(u)
    except Exception as e: print(f'ERROR {u}: {e}'); continue
    if f.exists():
        old=f.read_text()
        if old!=new:
            changed+=1; print(f'CHANGED {u}')
            print('\n'.join(list(difflib.unified_diff(old.splitlines(),new.splitlines(),lineterm='',n=0))[:60]))
        else: print(f'same    {u}')
    else: print(f'new     {u}')
    f.write_text(new)
sys.exit(1 if changed else 0)
