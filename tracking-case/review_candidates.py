"""Experimental review candidates, not confirmed errors or FrameGuard integration."""
import argparse
import csv
import json
import math
from pathlib import Path


def valid_box(box):
    return (isinstance(box,(list,tuple)) and len(box)==4
            and all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in box)
            and box[2]>box[0] and box[3]>box[1])

def near_edge(box,width,height,margin=0.04):
    return box[0]<=width*margin or box[1]<=height*margin or box[2]>=width*(1-margin) or box[3]>=height*(1-margin)

def candidates(frames,anchors,width,height,threshold=.85):
    if not (isinstance(width,(int,float)) and isinstance(height,(int,float)) and width>0 and height>0 and math.isfinite(width) and math.isfinite(height)):
        raise ValueError('positive finite image dimensions required')
    if not 0<threshold<1: raise ValueError('threshold must be between 0 and 1')
    if not isinstance(anchors,dict) or len(anchors)<2: raise ValueError('at least two anchors required')
    if any(not isinstance(k,int) or isinstance(k,bool) or not valid_box(v) for k,v in anchors.items()): raise ValueError('invalid anchor')
    keys=sorted(anchors); results=[]; seen=set()
    for f in frames:
        i=f['index'];box=f.get('bbox');occluded=f.get('occluded')
        if not isinstance(i,int) or isinstance(i,bool) or i in seen: raise ValueError('frame index must be a unique integer')
        if occluded is not None and type(occluded) is not bool: raise ValueError('occluded must be true, false or null')
        seen.add(i); row={'index':i,'status':'skipped','reason':'','height_ratio':None}
        if i in anchors: row['reason']='anchor'
        elif not valid_box(box): row['reason']='missing_or_invalid_box'
        elif occluded is True: row['reason']='known_occlusion'
        elif i<keys[0] or i>keys[-1]: row['reason']='outside_anchor_range'
        else:
            lo=max(k for k in keys if k<i);hi=min(k for k in keys if k>i)
            if any(near_edge(b,width,height) for b in (box,anchors[lo],anchors[hi])):
                row['reason']='near_edge'
            else:
                t=(i-lo)/(hi-lo); left=anchors[lo][3]-anchors[lo][1];right=anchors[hi][3]-anchors[hi][1]
                expected=left*(1-t)+right*t;ratio=(box[3]-box[1])/expected
                row.update(height_ratio=round(ratio,4),status='review' if ratio<threshold else 'no_flag',reason='height_below_baseline' if ratio<threshold else 'height_not_below_threshold')
                if occluded is None: row['reason']+=';occlusion_unknown'
        results.append(row)
    return results

def main():
    ap=argparse.ArgumentParser(description='Produce review candidates from local predictions; no automatic error verdict.')
    ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    try:
        data=json.loads(Path(args.input).read_text(encoding='utf-8-sig'))
        anchors={int(k):v for k,v in data['anchors'].items()}
        rows=candidates(data['frames'],anchors,data['width'],data['height'])
        out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
        with out.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['index','status','reason','height_ratio']);w.writeheader();w.writerows(rows)
        print(json.dumps({s:sum(r['status']==s for r in rows) for s in ('review','no_flag','skipped')},ensure_ascii=False))
    except (OSError,ValueError,KeyError,TypeError) as e:ap.exit(2,f'Input error: {e}\n')
if __name__=='__main__':main()
