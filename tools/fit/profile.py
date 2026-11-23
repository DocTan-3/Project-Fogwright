import json, numpy as np
D=json.load(open('aurelan_sil.json'))
def prof(front, side, n=240):
    F=D[front]; S=D[side]
    H=F['bot']-F['top']; rowsF=F['rows']
    cx=np.mean([ (r[0][0]+r[-1][1])/2 for r in rowsF[:40]])     # the head gives the centre line
    def frow(t):  # t: 0 feet .. 1 crown
        return rowsF[int(round((1-t)*(len(rowsF)-1)))]
    out=dict(t=[],torso=[],nruns=[],legL=[],legR=[],front=[],back=[])
    Hs=S['bot']-S['top']; rowsS=S['rows']
    # side reference: centre of the leg at knee height
    def srow(t): return rowsS[int(round((1-t)*(len(rowsS)-1)))]
    kr=srow(0.285); kx=(min(a for a,b in kr)+max(b for a,b in kr))/2
    for i in range(n+1):
        t=i/n; r=frow(t)
        c=[ru for ru in r if ru[0]<=cx<=ru[1]]
        out['t'].append(t); out['nruns'].append(len(r))
        out['torso'].append(((c[0][1]-c[0][0])/2/H) if c else None)
        L=[ru for ru in r if ru[1]<cx]; Rr=[ru for ru in r if ru[0]>cx]
        def legrun(lst, side):
            if not lst: return None
            ru=max(lst,key=lambda q:-abs((q[0]+q[1])/2-cx)) if False else min(lst,key=lambda q:abs((q[0]+q[1])/2-cx))
            return [((ru[0]+ru[1])/2-cx)/H, (ru[1]-ru[0])/2/H]
        out['legL'].append(legrun(L,'L')); out['legR'].append(legrun(Rr,'R'))
        s=srow(t); fx=max(b for a,b in s); bx=min(a for a,b in s)   # figure faces +x: front is the max
        out['front'].append((fx-kx)/Hs); out['back'].append((bx-kx)/Hs)
    # landmarks
    t=np.array(out['t']); tor=np.array([v if v else 0 for v in out['torso']])
    crotch=max(tt for tt,v,l in zip(t,out['torso'],out['legL']) if v is None and l is not None and tt<0.6) if any(v is None for v in out['torso']) else 0.47
    # armpit: highest row below 0.85 where the arms are separate from the body (3+ runs)
    arm=max(tt for tt,nr in zip(t,out['nruns']) if nr>=3 and 0.5<tt<0.85)
    neck=min((v,tt) for tt,v in zip(t,tor) if 0.78<tt<0.9 and v>0)[1]
    out['marks']=dict(crotch=float(crotch),armpit=float(arm),neck=float(neck))
    return out
res={'m':prof('m_front','m_side'),'f':prof('f_front','f_side')}
for k,v in res.items():
    print(k,v['marks'])
    for tt in [0.3,0.45,0.55,0.6,0.65,0.7,0.75,0.8,0.85]:
        i=int(tt*240); print(f'  t{tt:.2f} torso {v["torso"][i]} front {v["front"][i]:.3f} back {v["back"][i]:.3f} legL {v["legL"][i]}')
json.dump(res,open('aurelan_profile.json','w'))
