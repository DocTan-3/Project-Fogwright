# Greyscale detail maps for the palette materials that had none (godot/assets/library/<Key>_detail.png): the palette
# colours them, so each only carries grain. Mean brightness 0.78, like the kit's own maps.   python3 details.py
import numpy as np, os
from PIL import Image
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','godot','assets','library'); N=512; R=np.random.default_rng(7)
def smooth(a,k):   # tileable blur by repeated averaging with wrapped neighbours
    for _ in range(k): a=(a+np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1))/5
    return a
def noise(scale,k): return smooth(R.random((N,N)),k)*scale
def save(name,a,contrast):
    a=(a-a.mean())/(a.std()+1e-6)*contrast+0.78; Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8),'L').save(os.path.join(OUT,name+'_detail.png'))
y,x=np.mgrid[0:N,0:N]/N
straw=smooth(R.random((N,N))*np.ones((N,1)),0); straw=smooth(np.repeat(R.random((N,1)),N,1).T*0+np.repeat(R.random((1,N)),N,0),1)
save('Thatch',straw*0.7+noise(1,3)*0.3+0.15*np.sin(y*2*np.pi*24),0.16)       # vertical straw stalks, rows of bundles
save('Cloth',np.sin(x*2*np.pi*128)*np.sin(y*2*np.pi*128)*0.5+noise(1,2),0.06)   # a fine weave
save('Rope',np.sin((x+y)*2*np.pi*48)+noise(1,2)*0.6,0.12)                       # twisted strands
save('Iron',noise(1,4)+noise(1,1)*0.4,0.06)                                       # dull hammered metal
save('Fish',np.sin(x*2*np.pi*64+np.sin(y*2*np.pi*64)*1.5)+noise(1,2)*0.5,0.08)  # small scales
save('Glow',noise(1,6),0.02)
save('sea',noise(1,8),0.03)                                                     # still water: almost plain
save('earth',noise(1,3)+noise(1,8)*1.5,0.1)                                       # clods
# ground: grass clumps and blades; paths: packed dirt with pebbles, wheel ruts and footworn patches
blades=np.zeros((N,N))
for _ in range(9000):
    cx,cy=R.integers(0,N,2); L=R.integers(4,14); dx=R.normal(0,0.35)
    for t in range(L): blades[(cy-t)%N,int(cx+dx*t)%N]+=R.uniform(0.5,1.0)
save('Grass',smooth(blades,1)*0.6+noise(1,6)*1.2+noise(1,18)*1.6,0.14)
peb=np.zeros((N,N))
for _ in range(1400):
    cx,cy=R.integers(0,N,2); r=R.integers(1,4)
    for dy in range(-r,r+1):
        for dx in range(-r,r+1):
            if dx*dx+dy*dy<=r*r: peb[(cy+dy)%N,(cx+dx)%N]=R.uniform(0.6,1.0)
ruts=0   # no ruts: the detail tiles in world space, so stripes would run across paths, not along them
save('Path',smooth(peb,1)*0.9+noise(1,3)*0.5+noise(1,14)*1.4-ruts,0.12)
print('saved 10 detail maps')
