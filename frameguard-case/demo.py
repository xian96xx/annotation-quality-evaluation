"""A new synthetic teaching example, not the private FrameGuard implementation."""
import csv
from pathlib import Path

WIDTH, HEIGHT = 640, 360

def demo_sequence():
    """Generated rectangles only; no images or external/company annotations."""
    boxes = [[50+i*5, 80, 90+i*5, 120] for i in range(10)]
    boxes[2] = [-5,80,35,120]       # out of bounds
    boxes[5] = [400,80,440,120]    # unexpected jump; return is a second warning
    boxes[8] = [100,80,100,120]    # invalid geometry
    return boxes

def inspect(boxes, width=WIDTH, height=HEIGHT, jump_threshold=120):
    issues=[]
    previous=None
    for frame, box in enumerate(boxes):
        x1,y1,x2,y2=box
        if x1 >= x2 or y1 >= y2:
            issues.append((frame,'invalid_geometry','确定性错误'))
            previous=None
            continue
        if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
            issues.append((frame,'out_of_bounds','确定性错误'))
            previous=None
            continue
        center=((x1+x2)/2,(y1+y2)/2)
        if previous is not None:
            distance=((center[0]-previous[0])**2+(center[1]-previous[1])**2)**0.5
            if distance > jump_threshold:
                issues.append((frame,'large_jump','疑似异常，需人工复核'))
        previous=center
    return issues

def main():
    issues=inspect(demo_sequence())
    out=Path('reports');out.mkdir(exist_ok=True)
    with (out/'synthetic_findings.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['frame_zero_based','type','status']);w.writerows(issues)
    for row in issues: print(*row,sep=' | ')
    print(f'total {len(issues)}; synthetic sequence only')

if __name__=='__main__': main()
