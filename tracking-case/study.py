"""Synthetic interpolation study: no images, external data, or labeling files."""
from pathlib import Path
import csv

def truth(t):
    # Synthetic target accelerates toward the middle and changes width.
    center=100 + 4*t + 1.2*t*t
    width=40 + 0.8*t*t
    return center-width/2, center+width/2

def interpolate(t, anchors):
    if t in anchors: return truth(t)
    lo=max(a for a in anchors if a<t); hi=min(a for a in anchors if a>t)
    ratio=(t-lo)/(hi-lo); a=truth(lo); b=truth(hi)
    return tuple(a[i]+ratio*(b[i]-a[i]) for i in (0,1))

def edge_error(a,b):
    return max(abs(a[0]-b[0]),abs(a[1]-b[1]))

def study():
    results=[]
    for t in range(11):
        ref=truth(t)
        for name,anchors in [('two_anchors',(0,10)),('three_anchors',(0,5,10))]:
            estimate=interpolate(t,anchors)
            results.append({'frame':t,'strategy':name,'left':round(estimate[0],2),'right':round(estimate[1],2),'reference_left':round(ref[0],2),'reference_right':round(ref[1],2),'max_edge_error_px':round(edge_error(estimate,ref),2)})
    return results

def chart(rows):
    colors={'two_anchors':'#d46a35','three_anchors':'#216eab'}
    line=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 340" role="img" aria-label="Synthetic maximum edge error by frame">', '<rect width="720" height="340" fill="#fff"/>','<text x="70" y="27" font-family="sans-serif" font-size="18">Synthetic interpolation: maximum edge error (px)</text>','<path d="M70 55 V270 H660" stroke="#42506a" fill="none"/>']
    for val in (0,10,20,30,40):
        y=270-val*5
        line.append(f'<path d="M70 {y} H660" stroke="#e2e8f0"/><text x="35" y="{y+4}" font-family="sans-serif" font-size="12">{val}</text>')
    for t in range(11):
        x=70+t*59;line.append(f'<text x="{x-4}" y="290" font-family="sans-serif" font-size="12">{t}</text>')
    for name,color in colors.items():
        pts=' '.join(f"{70+r['frame']*59},{270-r['max_edge_error_px']*5}" for r in rows if r['strategy']==name)
        line.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/>')
    line.append('<text x="80" y="318" font-family="sans-serif" fill="#d46a35">Orange: frames 0 and 10 anchors</text><text x="370" y="318" font-family="sans-serif" fill="#216eab">Blue: add anchor at frame 5</text></svg>')
    return ''.join(line)

def main():
    rows=study();p=Path('reports');p.mkdir(exist_ok=True)
    with (p/'synthetic_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (p/'error_chart.svg').write_text(chart(rows),encoding='utf8')
    for name in ('two_anchors','three_anchors'):
        values=[r['max_edge_error_px'] for r in rows if r['strategy']==name]
        print(name,'mean=',round(sum(values)/len(values),2),'max=',max(values),'n=',len(values))
if __name__=='__main__':main()
