# Gather draped garments (drape.py's JSON, one per body) into creator/drapes.js:  python3 packdrapes.py out.js m:longcoat:a.json f:longcoat:b.json ...
import json,sys
out={}
for a in sys.argv[2:]:
    sex,name,path=a.split(':',2); g=json.load(open(path)); out.setdefault(sex,{})[name]=g
open(sys.argv[1],'w').write('// draped garments, made offline by tools/blender/drape.py (Blender cloth on each body at rest) and packed by packdrapes.py\nconst EQ_DRAPES='+json.dumps(out,separators=(',',':'))+';\n')
