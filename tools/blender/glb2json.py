import json,struct,base64,sys
d=open(sys.argv[1],'rb').read(); off=12; j=None; b=None
while off<len(d):
    ln,typ=struct.unpack('<II',d[off:off+8]); chunk=d[off+8:off+8+ln]; off+=8+ln
    if typ==0x4E4F534A: j=json.loads(chunk)
    elif typ==0x004E4942: b=chunk
j['buffers'][0]['uri']='data:application/octet-stream;base64,'+base64.b64encode(b).decode()
open(sys.argv[2],'w').write(json.dumps(j,separators=(',',':')))
