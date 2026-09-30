"""Offline mosaic preparation / post composition; no network writes."""
import argparse,json,subprocess
from pathlib import Path

def units(s): return len(s.encode('utf-16-le'))//2

def compose(m,before='',after='',entities=None):
    cols,rows,ids=m['columns'],m['rows'],m['emoji_ids']
    if not 1<=cols<=9 or rows<1 or len(ids)!=cols*rows or len(ids)>200 or not all(str(x).isdigit() for x in ids):
        raise ValueError('Invalid geometry/IDs')
    text=before+('\n' if before else '')+'\u200b'; out=list(entities or [])
    for e in out:
        if e['offset']<0 or e['offset']+e['length']>units(before): raise ValueError('Entity outside before text')
    for i,eid in enumerate(ids):
        out.append({'type':'custom_emoji','offset':units(text),'length':2,'custom_emoji_id':str(eid)})
        text+='🎨'
        if i%cols==cols-1 and i<len(ids)-1: text+='\n'
    if after:text+='\n'+after
    if units(text)>4096:raise ValueError('Split explicitly; never truncate')
    return {'text':text,'entities':out}

def prepare(source,output,cols=9,rows=11,step=80,margin=20):
    if not 1<=cols<=9 or rows<1 or cols*rows>200 or not 1<=step<=100:raise ValueError('Invalid geometry')
    w,h=cols*100,rows*step
    if not 0<=margin<min(w,h)//2:raise ValueError('Invalid margin')
    source=Path(source).resolve();p=Path(output).resolve()
    if not source.is_file():raise ValueError('Missing source')
    p.mkdir(parents=True,exist_ok=True);t=p/'tiles';t.mkdir(exist_ok=True)
    if any(t.iterdir()) or (p/'manifest.json').exists():raise ValueError('Use fresh output directory')
    def run(a):subprocess.run(['convert']+a,check=True)
    # Square fit reproduces accepted mascot preset; never force-resize/crop.
    fit=min(w,h)-2*margin
    run([str(source),'-resize',f'{fit}x{fit}','-gravity','center','-background','none','-extent',f'{w}x{h}',str(p/'source.png')])
    run([str(p/'source.png'),'-crop',f'100x{step}','+repage',str(t/'tile-%03d.png')])
    fs=sorted(t.glob('*.png'))
    if len(fs)!=cols*rows:raise ValueError('Incorrect tile count')
    for f in fs:
        run([str(f),'-gravity','center','-background','none','-extent','100x100','-define','webp:lossless=true',str(f.with_suffix('.webp'))])
        if f.with_suffix('.webp').stat().st_size>512*1024:raise ValueError('Tile too large')
    m={'columns':cols,'rows':rows,'content_height':step,'margin':margin,'tile_count':len(fs),'emoji_ids':[],'visual_status':'local_preview_only'}
    (p/'manifest.json').write_text(json.dumps(m,indent=2));return m

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('prepare');a.add_argument('source');a.add_argument('output')
    a.add_argument('--columns',type=int,default=9);a.add_argument('--rows',type=int,default=11);a.add_argument('--content-height',type=int,default=80);a.add_argument('--margin',type=int,default=20)
    c=s.add_parser('compose');c.add_argument('manifest');c.add_argument('output');c.add_argument('--before-file');c.add_argument('--after-file');c.add_argument('--entities-file')
    x=p.parse_args();read=lambda f:Path(f).read_text() if f else ''
    if x.command=='prepare':print(json.dumps(prepare(x.source,x.output,x.columns,x.rows,x.content_height,x.margin)))
    else:
        r=compose(json.loads(read(x.manifest)),read(x.before_file),read(x.after_file),json.loads(read(x.entities_file)) if x.entities_file else [])
        Path(x.output).write_text(json.dumps(r,ensure_ascii=False,indent=2));print('entities',len(r['entities']))
if __name__=='__main__':main()
