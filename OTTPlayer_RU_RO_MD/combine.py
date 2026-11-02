#!/usr/bin/env python3
"""Combine freely available public streams into one IPTV M3U playlist."""
from urllib.request import Request, urlopen
from urllib.error import URLError
import re
from pathlib import Path

SOURCES = [
    ('Rusa', 'https://iptv-org.github.io/iptv/languages/rus.m3u'),
    ('Romana', 'https://iptv-org.github.io/iptv/languages/ron.m3u'),
    ('Moldova', 'https://iptv-org.github.io/iptv/countries/md.m3u'),
]
OUT = Path(__file__).parent / 'playlist.m3u'

def read_source(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 IPTV-combiner/1.0'})
    with urlopen(request, timeout=45) as response:
        return response.read().decode('utf-8-sig', errors='replace')

def parse(content):
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if line.startswith('#EXTINF:'):
            opts=[]
            j=idx+1
            while j<len(lines) and lines[j].startswith('#') and not lines[j].startswith('#EXTINF:'):
                opts.append(lines[j]); j+=1
            if j<len(lines) and lines[j].strip() and not lines[j].startswith('#'):
                yield line, opts, lines[j].strip()

def main():
    seen=set(); output=['#EXTM3U']; n=0; errors=[]
    for group,url in SOURCES:
        try:
            entries=list(parse(read_source(url)))
        except (OSError, URLError, ValueError) as exc:
            errors.append(f'{group}: {exc}')
            continue
        for info,opts,stream in entries:
            if stream in seen: continue
            seen.add(stream)
            # Override original group-title so OTTPlayer shows clear language groups.
            info = re.sub(r'\s+group-title="[^"]*"', '', info)
            info = info.replace('#EXTINF:', f'#EXTINF: group-title="{group}"', 1)
            output.extend([info, *opts, stream]); n+=1
    if n == 0:
        raise RuntimeError('No streams fetched; existing file preserved. ' + '; '.join(errors))
    OUT.write_text('\n'.join(output)+'\n', encoding='utf-8')
    print(f'Created {OUT.name} with {n} unique streams. ' + '; '.join(errors))

if __name__=='__main__': main()
