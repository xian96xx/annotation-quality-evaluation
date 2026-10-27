"""Fetch one explicitly named USC annotation from the official archive by HTTP Range.
The downloaded third-party material stays in local/ (gitignored).
"""
import io, time, urllib.request, zipfile
from pathlib import Path

URL = 'https://huggingface.co/datasets/uscmcl/MCL_drone_dataset/resolve/main/usc%20drone-001.zip'
SIZE = 3947630639
MEMBER = 'Drone_frames/img/groundtruth_rect.txt'
class RangeReader(io.RawIOBase):
    def __init__(self): self.pos=0; self.start=-1; self.cache=b''
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else SIZE+offset
        return self.pos
    def read(self,n=-1):
        if n<0: n=SIZE-self.pos
        if n==0: return b''
        if self.start<=self.pos and self.pos+n<=self.start+len(self.cache):
            i=self.pos-self.start; self.pos+=n; return self.cache[i:i+n]
        start=self.pos; end=min(SIZE-1,start+max(n,524288)-1)
        error=None
        for attempt in range(3):
            try:
                request=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}','User-Agent':'public-quality-case/1.0'})
                with urllib.request.urlopen(request,timeout=25) as response:
                    if response.status!=206: raise ValueError('server did not honor range')
                    data=response.read()
                if len(data)!=end-start+1: raise ValueError('range size mismatch')
                self.start=start;self.cache=data;self.pos+=n;return data[:n]
            except (OSError,ValueError) as e:
                error=e;time.sleep(attempt+1)
        raise RuntimeError('source or range service unavailable; retry later') from error

def main():
    EXPECTED_SHA256 = "2473a0a2d8d1a4f5cd5544e69dd120436393737189b4fdcfc27bf627844877b7"
    import hashlib
    with zipfile.ZipFile(RangeReader()) as archive:
        info=archive.getinfo(MEMBER)
        if info.file_size>1024*1024: raise ValueError('unexpected member size')
        data=archive.read(info)
    if hashlib.sha256(data).hexdigest()!=EXPECTED_SHA256:
        raise ValueError('source file hash differs; re-check version and provenance')
    out=Path('local/usc_groundtruth_rect.txt');out.parent.mkdir(exist_ok=True)
    out.write_bytes(data);print('Downloaded verified public reference file to local/ (not for commit).')
if __name__=='__main__':main()
