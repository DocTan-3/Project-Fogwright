# Fitting bodies to a reference sheet

1. `measure.py`: splits a turnaround sheet (front and side views of a man and a woman on a flat grey background) into four silhouettes. Edit `PANELS` for the sheet's layout.
2. `profile.py`: turns the silhouettes into widths and front/back outlines at every height, with crotch, armpit and neck landmarks. Writes `<people>_profile.json`.
3. Build the fitted bodies, then merge each as that people's shape:

```sh
FIT=tools/fit/aurelan_profile.json FITSEX=m RACE=human  python rpgbody.py -- aurelan_m.glb
FIT=tools/fit/aurelan_profile.json FITSEX=f RACE=female python rpgbody.py -- aurelan_f.glb
python merge_peoples.py rpgbody.glb male.glb Ferrin=ferrin.glb Ilvari=ilvari.glb Zarhim=zarhim.glb Aurelan=aurelan_m.glb
python merge_peoples.py female.glb female_m.glb Aurelan=aurelan_f.glb
```

The fit matches the torso width (crotch to armpit), each leg's width, and the side outline (chest, back, glutes, legs). Heights are aligned by crotch and neck. It also fits the shoulder width (moving the arms and their bones to match) and each arm's thickness along its length, corrected for the arms hanging at a different angle than on the sheet. Head, hands and feet are left as they are.
