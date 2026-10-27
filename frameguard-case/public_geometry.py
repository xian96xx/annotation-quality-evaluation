"""Geometry-only independent reproduction on sparse USC reference boxes."""
import argparse,hashlib,json,math
from pathlib import Path
EXPECTED_SHA256='2473a0a2d8d1a4f5cd5544e69dd120436393737189b4fdcfc27bf627844877b7'
def geometry(boxes,width=1920,height=1080):
 issues=[]
 for i,(x,y,w,h) in enumerate(boxes):
  if not all(math.isfinite(v) for v in (x,y,w,h)) or w<=0 or h<=0:issues.append((i,'invalid_geometry'))
  elif x<0 or y<0 or x+w>width or y+h>height:issues.append((i,'out_of_bounds'))
 return issues

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--annotation',required=True);args=ap.parse_args(); data=Path(args.annotation).read_bytes()
 if hashlib.sha256(data).hexdigest()!=EXPECTED_SHA256:ap.error('reference hash mismatch')
 boxes=[[float(v) for v in row.split(',')] for row in data.decode('utf-8-sig').splitlines() if row.strip()][:5]
 if len(boxes)!=5 or any(len(b)!=4 for b in boxes):ap.error('unexpected reference format')
 changed=[b[:] for b in boxes];changed[2][0]=-1
 print(json.dumps({'reference_boxes':len(boxes),'unmodified_findings':geometry(boxes),'injected_findings':geometry(changed),'note':'geometry only; index 2 corresponds to source frame 31'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
