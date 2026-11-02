#!/usr/bin/env python3
"""Find public IPTV-org streams for an explicit StarNet-style target list.
A candidate found in an index does not imply its playback works in the UK.
"""
import csv, difflib, io, re, unicodedata
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
SRC = 'https://iptv-org.github.io/iptv/index.m3u'
OUT = ROOT / 'playlist_starnet.m3u'
REPORT = ROOT / 'starnet_report.csv'

# Canonicalizations improve matches without silently equating unrelated channels.
ALIAS = {
    'tnt international':['tnti','tnt international'],
    'sts international':['stsi','sts international'],
    'pyatnitsa international':['friday international','pyatnitsa'],
    'domashniy international':['domashniy international'],
    'viju tv1000 russkoe':['tv1000 russian cinema','tv1000 russkoe kino','viju tv1000 russkoe'],
    'acasa':['acasa tv','acasa'],
    'mosfilm':['mosfilm zolotaya kollektsiya','mosfilm'],
    'match planeta':['match planeta'],
    'mult':['mult tv'],
    'shanson tv':['chanson tv','shanson tv'],
    'kinohit':['kinohit','kino hit'],
    'kinomix':['kinomix','kino mix'],
    'kinosemya':['kinosemya','kino semya'],
    'kinoseriya':['kinoseriya','kino seriya'],
    'kinokomediya':['kinokomediya','kino komediya'],
}

CYR = str.maketrans({'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'})
def norm(s):
    s = s.lower().translate(CYR)
    s = ''.join(ch for ch in unicodedata.normalize('NFKD',s) if not unicodedata.combining(ch))
    s = re.sub(r'\b(hd|sd|fhd|uhd|1080p|720p|576p|480p)\b',' ',s)
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def get_source():
    req=Request(SRC,headers={'User-Agent':'Mozilla/5.0'})
    with urlopen(req,timeout=50) as r:
        return r.read().decode('utf-8-sig','replace')

def parse_m3u(body):
    result=[]; meta=None; extra=[]
    for raw in body.splitlines():
        s=raw.strip()
        if s.startswith('#EXTINF:'):
            meta=s;extra=[]
        elif s.startswith('#EXTVLCOPT:') or s.startswith('#KODIPROP:'):
            extra.append(s)
        elif s and not s.startswith('#') and meta:
            name=meta.rsplit(',',1)[-1].strip()
            idmatch=re.search(r'tvg-id="([^"]*)"',meta)
            result.append((name,idmatch.group(1) if idmatch else '',meta,tuple(extra),s))
            meta=None;extra=[]
    return result

def matching(target,items):
    aliases=[norm(target)]+[norm(x) for x in ALIAS.get(norm(target),[])]
    matches=[]
    for name,tvg,meta,extra,url in items:
        k=norm(name);t=norm(tvg.split('@')[0].split('.')[0])
        # Deliberately strict: no fuzzy accidental 'TV8' => 'TV80'.
        if any(a==k or a==t or (len(a)>5 and k.startswith(a+' ')) for a in aliases if a):
            matches.append((name,tvg,meta,extra,url))
    return matches

def main():
    with (ROOT/'starnet_targets.csv').open(encoding='utf-8-sig',newline='') as f:
        targets=list(csv.DictReader(f))
    items=parse_m3u(get_source())
    lines=['#EXTM3U'];report=[];seen=set()
    for row in targets:
        matches=matching(row['name'],items)
        added=0
        for name,tvg,old,extra,url in matches:
            if url in seen: continue
            seen.add(url)
            logo=re.search(r'tvg-logo="([^"]*)"',old)
            logo_val=logo.group(1) if logo else ''
            clean_name=name.replace('"','')
            lines.append(f'#EXTINF:-1 tvg-id="{tvg}" tvg-logo="{logo_val}" group-title="{row["category"]}",{clean_name}')
            lines.extend(extra)
            lines.append(url)
            added+=1
        report.append({'category':row['category'],'channel':row['name'],'candidate_streams':added,'status':'FOUND_UNTESTED' if added else 'NOT_FOUND'})
    OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    with REPORT.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['category','channel','candidate_streams','status']);w.writeheader();w.writerows(report)
    print(f'Targets: {len(targets)} | indexed streams: {len(items)} | targets with candidates: {sum(r["candidate_streams"]>0 for r in report)} | candidate links: {len(seen)}')
    print('IMPORTANT: FOUND_UNTESTED means indexed, not verified in UK.')

if __name__=='__main__':main()
