"""Build review-only edge proposals; this script never modifies annotation files."""
import argparse
import json
import math
from pathlib import Path

def _number(n):
    return isinstance(n,(int,float)) and not isinstance(n,bool) and math.isfinite(n)

def _valid_box(box,width,height):
    return (isinstance(box,(list,tuple)) and len(box)==4 and all(_number(x) for x in box)
            and 0<=box[0]<box[2]<=width and 0<=box[1]<box[3]<=height)

def propose(original,source,edge,width,height,*,is_anchor=False,max_fraction=.1):
    """Change only the human-selected edge; reject anchors, invalid or large moves."""
    if type(is_anchor) is not bool: raise ValueError('is_anchor must be boolean')
    if is_anchor: raise ValueError('anchors cannot be modified')
    if not (_number(width) and _number(height) and width>0 and height>0): raise ValueError('invalid image dimensions')
    if not (_number(max_fraction) and 0<max_fraction<=.2): raise ValueError('invalid max_fraction')
    if not (_valid_box(original,width,height) and _valid_box(source,width,height)): raise ValueError('invalid or out-of-bounds box')
    if edge not in ('left_expand','top_shrink'): raise ValueError('unsupported edge or direction')
    k=0 if edge=='left_expand' else 1
    delta=source[k]-original[k]
    if (edge=='left_expand' and delta>=0) or (edge=='top_shrink' and delta<=0):
        raise ValueError('source edge is not in requested direction')
    dimension=(original[2]-original[0]) if k==0 else (original[3]-original[1])
    if abs(delta)>dimension*max_fraction: raise ValueError('edge move exceeds bound')
    result=list(original);result[k]=source[k]
    if not _valid_box(result,width,height): raise ValueError('proposal invalid')
    return {'status':'pending_human_review','edge':edge,'box':result,'delta_px':round(delta,3)}

def main():
    ap=argparse.ArgumentParser(description='Create review-only proposals in a new JSON file')
    ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    try:
        src=Path(a.input).resolve();dst=Path(a.out).resolve()
        if src==dst: raise ValueError('output must not equal input')
        data=json.loads(src.read_text(encoding='utf-8-sig'))
        results=[];seen=set()
        for item in data['items']:
            key=item['frame']
            if not isinstance(key,int) or isinstance(key,bool) or key in seen: raise ValueError('frame must be a unique integer')
            seen.add(key)
            entry=propose(item['original'],item['source'],item['edge'],data['width'],data['height'],is_anchor=item['is_anchor'],max_fraction=item.get('max_fraction',.1))
            entry['frame']=key;results.append(entry)
        if not results: raise ValueError('no proposals')
        dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('x',encoding='utf8') as f:json.dump({'proposals':results},f,ensure_ascii=False,indent=2)
        print(f'{len(results)} proposals saved; none applied')
    except (OSError,KeyError,TypeError,ValueError) as e:ap.exit(2,f'Input error: {e}\n')
if __name__=='__main__':main()
