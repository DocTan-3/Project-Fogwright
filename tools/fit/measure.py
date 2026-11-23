import numpy as np, json, sys
from PIL import Image
from scipy import ndimage
im=np.asarray(Image.open('aurelan.webp').convert('RGB')).astype(int)
mask=(im[:,:,0]-im[:,:,2])>14
PANELS={'m_front':(40,560),'m_side':(560,960),'f_front':(960,1460),'f_side':(1460,1900)}
out={}
for k,(x0,x1) in PANELS.items():
    m=mask[175:1110,x0:x1].copy()
    lab,n=ndimage.label(m); sizes=ndimage.sum(m,lab,range(1,n+1)); big=1+int(np.argmax(sizes))
    m=ndimage.binary_closing(ndimage.binary_fill_holes(lab==big),iterations=2)
    ys=np.where(m.any(1))[0]; top,bot=ys[0],ys[-1]
    rows=[]
    for y in range(top,bot+1):
        xs=np.where(m[y])[0]
        # runs
        runs=[]; s=xs[0]; p=xs[0]
        for x in xs[1:]:
            if x!=p+1: runs.append((s,p)); s=x
            p=x
        runs.append((s,p)); rows.append(runs)
    out[k]=dict(top=int(top),bot=int(bot),rows=[[ [int(a)+x0,int(b)+x0] for a,b in r] for r in rows])
    Image.fromarray((m*255).astype(np.uint8)).save(f'mask_{k}.png')
    print(k,'height px',bot-top,'runs at 25/50/75%',[len(rows[int(len(rows)*f)]) for f in (0.25,0.5,0.75)])
json.dump(out,open('aurelan_sil.json','w'))
