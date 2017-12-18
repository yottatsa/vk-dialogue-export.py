import json
import glob
import os
import urllib2
import tempfile

def fetch(base, fn, url, t):
    if not os.path.exists(fn):
        print fn
        f = tempfile.NamedTemporaryFile(dir=base, delete=False)
        f.write(urllib2.urlopen(url).read())
        os.rename(f.name, fn)
        f.close()
    if t:
        print fn, t
        os.utime(fn, (t, t))

def download(base, msg):
    for i, att in enumerate(msg['attachments'], 1):
        t = att['type']
        if t == 'photo':
            url = att[t].get('src_xxxbig') or att[t].get('src_xxbig') or att[t].get('src_xbig') or att[t].get('src_big')
            fn = os.path.basename(url)
            t = att[t].get('created')
        elif t == 'doc':
            url = att[t]['url']
            fn = att[t]['title'].encode('utf-8')
            t = att[t].get('doc')
        else:
            continue

        ffn = os.path.join(base, '{}_{}_{}'.format(msg['mid'], i, fn))
        fetch(base, ffn, url, t)

for fn in glob.glob('*.json'):
    with open(fn, 'r') as f:
        d = json.load(f)

    base = fn.replace('.json', '')
    if not os.path.exists(base):
        os.mkdir(base)

    for msg in d.get('messages', []):
        if 'attachments' in msg:
            download(base, msg)
