# The hair texture, made in code (no third-party source): python3 hairtex.py out.png
# Left half: the scalp cap - dense strands in clumps, running down v from the cap's pole to its hairline, ending in jagged
# tips (cut out by alpha). It wraps round in u. Right half: four locks (64 px each) - strands converging into split,
# pointed tips. Grey only: the game tints it with the hair colour.
import numpy as np,sys
from PIL import Image
W,H=1024,512; rng=np.random.default_rng(7)
def pnoise(u,freq,seed,oct=3):   # noise periodic in u (period 1), smooth in v-independent form
    r=np.random.default_rng(seed); out=np.zeros_like(u)
    for o in range(oct):
        f=freq*2**o; ph=r.uniform(0,1,f); a=r.uniform(-1,1,f)
        x=u*f; i=np.floor(x).astype(int)%f; j=(i+1)%f; t=x-np.floor(x); t=t*t*(3-2*t)
        out+=(a[i]*(1-t)+a[j]*t)/(2**o)
    return out
def smooth(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
img=np.zeros((H,W,4),np.float32)
# ---- the cap
v,u=np.mgrid[0:H,0:512]/np.array([H,512.])[:,None,None]
wob=0.012*pnoise(v[:,0],3,1)[:,None]+0.006*pnoise(v[:,0],9,11)[:,None]                        # clumps wander a little along their length
uw=u+0.025*pnoise(u[0],7,2)[None,:]+wob
cl=(uw*26)%1.0
clumpB=0.1*pnoise(np.floor(uw*26)/26+0.001,26,8,1)
gStr=0.35+0.65*(pnoise(np.floor(uw*26)/26+0.002,26,12,1)*0.5+0.5)**2   # how deep each clump's groove is   # each clump a little lighter or darker           # 12 clumps round
groove=(smooth(0.8,0.98,cl)+(1-smooth(0.0,0.06,cl))*0.5)*gStr
fine=0.5*pnoise(u[0],128,3)[None,:]+0.4*pnoise(u[0],320,4)[None,:]
val=0.8+0.24*fine-0.32*groove+clumpB+0.08*np.sin(cl*np.pi)+0.04*pnoise(v[:,0],8,5)[:,None]
val*=0.9+0.1*smooth(0.0,0.15,v)                              # a touch darker at the pole (roots, parting)
# the cut edge: clean, as a barber leaves it - one even line with a millimetre of strand-level variation, never ragged
jag=pnoise(u[0],480,7,2)[None,:]
alpha=(v<0.95+0.008*jag).astype(np.float32)
# two edges, each on a quarter of the sheet: [0, .25) ends in tips (a crop or a fringe: the hair ends at the hairline);
# [.25, .5) is a root edge (pulled-back hair grows from the hairline: fine short wisps, thinning and darkening to the scalp)
half=lambda a:a[:,::2]
img[:,0:256,0]=np.clip(half(val),0,1); img[:,0:256,3]=half(alpha)
rootThr=0.95+0.006*pnoise(u[0],600,31,2)[None,:]*np.ones_like(v)   # the hairline where hair grows: just as even; the body paint
rootVal=val*(1-0.06*smooth(0.86,1.0,v))                              # beneath it fades it softly into the skin
img[:,256:512,0]=np.clip(half(rootVal),0,1); img[:,256:512,3]=half((v<rootThr).astype(np.float32))
# ---- four locks
for k in range(4):
    x0=512+k*128; vv,s=np.mgrid[0:H,0:128]/np.array([H,128.])[:,None,None]
    r=np.random.default_rng(20+k); forks=[2,3,2,3][k]
    hw=0.5-0.06*smooth(0,0.3,vv)                              # the lock narrows a little below the root...
    alpha=np.zeros_like(vv); val=np.zeros_like(vv)
    centres=np.linspace(0.5-0.22,0.5+0.22,forks)+r.uniform(-0.04,0.04,forks)
    ends=r.uniform(0.86,0.99,forks)
    for c,e in zip(centres,ends):                              # ...and splits into forks that taper to points
        split=smooth(0.45,0.7,vv)
        cc=0.5+(c-0.5)*split
        w=(hw*(1-split)+(0.5/forks+0.04)*split)*np.clip((e-vv)/(e-0.55),0,1)**0.7
        d=np.abs(s-cc)
        edge=np.interp(vv[:,0],np.linspace(0,1,40),r.uniform(-0.08,0.08,40))[:,None]
        inside=d<w*(1+edge)
        alpha=np.maximum(alpha,inside)
        sl=np.where(w>1e-3,(s-cc)/np.maximum(w,1e-3),0)        # strands follow the taper
        st=0.5*np.sin(sl*11+k)+0.3*np.sin(sl*29+vv*5)+0.2*np.sin(sl*63+c*9)
        val=np.maximum(val,inside*(0.88+0.16*st-0.3*np.clip(np.abs(sl),0,1)**2))
    val*=0.88+0.12*smooth(0,0.12,vv)
    img[:,x0:x0+128,0]=np.clip(val,0,1); img[:,x0:x0+128,3]=alpha
img[:,:,1]=img[:,:,0]; img[:,:,2]=img[:,:,0]
Image.fromarray((img*255).astype(np.uint8),'RGBA').save(sys.argv[1])
print('wrote',sys.argv[1])
