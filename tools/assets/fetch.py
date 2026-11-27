# Download the free ("name your own price", paying nothing) asset packs listed in packs.json from itch.io:
#   python3 tools/assets/fetch.py <out dir> [name filter]
# Each pack goes into <out dir>/<page slug>/ as the zip(s) itch.io serves. Keep <out dir> outside the repository: only packs
# marked "repo": true may be committed, and then only the files Fogwright uses.
import sys,re,json,os,urllib.request,urllib.parse,http.cookiejar
here=os.path.dirname(os.path.abspath(__file__)); packs=json.load(open(os.path.join(here,'packs.json')))['packs']
out=sys.argv[1]; flt=sys.argv[2].lower() if len(sys.argv)>2 else ''
def fetch(page,dest):
    cj=http.cookiejar.CookieJar(); op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders=[('User-Agent','Mozilla/5.0 (X11; Linux x86_64)')]
    csrf=lambda h:re.search(r'name="csrf_token" value="([^"]+)"',h).group(1)
    h=op.open(page).read().decode()
    dl=json.loads(op.open(page+'/download_url',urllib.parse.urlencode({'csrf_token':csrf(h)}).encode()).read())['url']
    d=op.open(dl).read().decode()   # the download page (the key in its address expires within about a minute)
    for uid in sorted(set(re.findall(r'data-upload_id="(\d+)"',d))):
        j=json.loads(op.open(f"{page}/file/{uid}?source=view_game&as_props=1&after_download_lightbox=1",
                             urllib.parse.urlencode({'csrf_token':csrf(d)}).encode()).read())
        if 'url' not in j: print('  upload',uid,'not available:',j); continue
        with op.open(j['url']) as f: data=f.read()
        p=os.path.join(dest,f'{uid}.zip'); open(p,'wb').write(data); print('  saved',p,f'{len(data)/1e6:.1f} MB')
for p in packs:
    if flt and flt not in p['name'].lower(): continue
    slug=p['url'].rstrip('/').rsplit('/',1)[-1]; dest=os.path.join(out,slug); os.makedirs(dest,exist_ok=True)
    print(p['name'],'-',p['licence'],'' if p['repo'] else '- NOT for the public repo')
    if p.get('manual'): print('  manual download (a browser is needed):',p['url']); continue
    if p.get('direct'):   # a plain zip link
        try:
            req=urllib.request.Request(p['direct'],headers={'User-Agent':'Mozilla/5.0'}); data=urllib.request.urlopen(req).read()
            f=os.path.join(dest,os.path.basename(p['direct'])); open(f,'wb').write(data); print('  saved',f,f'{len(data)/1e6:.1f} MB')
        except Exception as e: print('  failed:',e)
        continue
    try: fetch(p['url'],dest)
    except Exception as e: print('  failed:',e)
