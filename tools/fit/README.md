# Fitting bodies to a reference sheet

1. `measure.py`: splits a turnaround sheet (front and side views of a man and a woman on a flat grey background) into four silhouettes. Edit `PANELS` for the sheet's layout.
2. `profile.py`: turns the silhouettes into widths and front/back outlines at every height, with crotch, armpit and neck landmarks. Writes `<people>_profile.json`.
3. Build the fitted bodies, then merge each as that people's shape:

```sh
FIT=tools/fit/aurelan_profile.json FITSEX=m RACE=human  python rpgbody.py -- aurelan_m.glb
FIT=tools/fit/aurelan_profile.json FITSEX=f RACE=female python rpgbody.py -- aurelan_f.glb
REST_FROM=aurelan_m.glb python merge_peoples.py rpgbody.glb male.glb Ferrin=ferrin.glb Ilvari=ilvari.glb Zarhim=zarhim.glb Aurelan=aurelan_m.glb
REST_FROM=aurelan_f.glb python merge_peoples.py female.glb female_m.glb Aurelan=aurelan_f.glb
```

The fit matches the torso width (crotch to armpit), each leg's width, and the side outline (chest, back, glutes, legs). Heights are aligned by crotch and neck. It also fits the shoulder width (moving the arms and their bones to match) and each arm's thickness along its length, corrected for the arms hanging at a different angle than on the sheet. Head, hands and feet are left as they are.

`REST_FROM` gives the merged model the fitted body's paint coordinates. On a fitted body the torso's paint heights are remapped by landmarks (waistband, knees, neck, and her bust apex onto the chest wrap), so the painted bands land on the fitted anatomy. The paint splits arm from torso by the rig's skin weights.

The arms hang out at the sheet's A-pose (`ARM_OUT`, 7 degrees). The weld runs with them further out (`WELD_OUT`, 12 degrees) so it cannot fill in the armpit, then swings them back. The swing fades to nothing where the source arm shells meet the torso, because those shells are open at the top and only the torso closes them. A rigid swing tears a hole there, and the weld then falls apart. The build stops if any point is left without skin weights.
