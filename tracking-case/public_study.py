"""Evaluate a simple interpolation baseline against five sparse USC reference boxes."""
import argparse, csv, hashlib, json
from pathlib import Path

EXPECTED_SHA256 = '2473a0a2d8d1a4f5cd5544e69dd120436393737189b4fdcfc27bf627844877b7'

def parse_boxes(data):
    rows=[]
    for line in data.decode('utf-8-sig').splitlines():
        if not line.strip(): continue
        parts=[float(x) for x in line.strip().split(',')]
        if len(parts)!=4 or parts[2]<=0 or parts[3]<=0: raise ValueError('expected positive x,y,w,h')
        x,y,w,h=parts; rows.append((x,y,x+w,y+h))
    if len(rows)<5: raise ValueError('at least five boxes required')
    return rows[:5]

def interpolate(a,b,weight): return tuple(x+(y-x)*weight for x,y in zip(a,b))
def iou(a,b):
    area=lambda q:max(0,q[2]-q[0])*max(0,q[3]-q[1])
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    return inter/(area(a)+area(b)-inter)

def compare(boxes):
    results=[]
    for index in (1,3):
        two=interpolate(boxes[0],boxes[4],index/4)
        lo,hi=(boxes[0],boxes[2]) if index==1 else (boxes[2],boxes[4])
        three=interpolate(lo,hi,.5); target=boxes[index]
        for method,box in [('two_anchors',two),('three_anchors',three)]:
            results.append({'frame_one_based':1+index*15,'method':method,'iou':round(iou(box,target),4),'max_edge_error_px':round(max(abs(a-b) for a,b in zip(box,target)),2)})
    return results

def main():
    ap=argparse.ArgumentParser(description='Requires an independently acquired USC dataset annotation file.')
    ap.add_argument('--annotation',required=True);ap.add_argument('--out',default='reports/public_comparison.csv');args=ap.parse_args()
    data=Path(args.annotation).read_bytes(); sha=hashlib.sha256(data).hexdigest()
    if sha!=EXPECTED_SHA256:ap.error('Input hash differs from the observed source file; stop and re-check provenance and format.')
    rows=compare(parse_boxes(data));out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
