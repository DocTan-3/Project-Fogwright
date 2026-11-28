# Writes the Windows preset's file list (godot/export_presets.cfg): only what the game uses goes into a build. Whole
# folders the game builds from by name (the village kit, our props, characters, materials), and from the big kits only
# the models the scripts or the plan data name. Godot adds their textures. Run before every export.
#   python3 tools/build/export_list.py
import os,re,glob
G=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','godot'); os.chdir(G)
src=''.join(open(f).read() for f in glob.glob('scripts/**/*.gd',recursive=True)+glob.glob('data/*.json'))
names=set(re.findall(r'"([A-Za-z][A-Za-z0-9_]+)"',src))|set(re.findall(r'/([A-Za-z][A-Za-z0-9_]+)\.(?:gltf|glb)"',src))   # bare names and full model paths
for pat in re.findall(r'"([A-Za-z_]+)%d"',src): names|={pat+str(i) for i in range(1,10)}   # CommonTree_%d and the like
keep=['res://'+f for d in ['assets/props/quaternius','assets/nature/quaternius'] for f in sorted(glob.glob(d+'/*.gltf'))
      if os.path.splitext(os.path.basename(f))[0] in names]
for d in ['assets/village/quaternius','assets/props/docks','assets/props/village2','assets/props/fogwright','assets/characters','assets/library','assets/buildings/medieval_voxel']:
    keep+=['res://'+f for f in sorted(glob.glob(d+'/**/*',recursive=True)) if f.endswith(('.gltf','.glb','.png'))]
keep+=['res://'+f for f in sorted(glob.glob('data/*.png'))]   # generated maps the level loads (the ground's path mask)
keep+=['res://assets/animations/quaternius/UAL1_Standard.glb','res://assets/animations/quaternius/UAL2_Standard.glb']   # UAL2: combat (sword combos, block, knockback, the enemies' clips)
keep+=['res://'+f for f in sorted(glob.glob('assets/voxel/baked/*.scn'))]   # the village's baked buildings (tools/build/bake_farhallow.sh)
keep+=['res://'+f for f in sorted(glob.glob('scenes/*.tscn')+glob.glob('scripts/**/*.gd',recursive=True))]
keep=[k.replace(os.sep,'/') for k in keep]   # glob gives backslashes on Windows
cfg=open('export_presets.cfg').read()
cfg=re.sub(r'export_filter="[^"]*"','export_filter="resources"',cfg,count=1)
cfg=re.sub(r'\nexport_files=PackedStringArray\([^)]*\)','',cfg)
cfg=cfg.replace('export_filter="resources"','export_filter="resources"\nexport_files=PackedStringArray(%s)'%', '.join('"%s"'%k for k in keep),1)
cfg=cfg.replace(', assets/animations/quaternius/UAL2*','')   # combat uses the second library
cfg=re.sub(r'include_filter="[^"]*"','include_filter="data/*.json, *.vox"',cfg,count=1)   # .vox files are read raw by Vox, not imported, so they ride in as plain files
open('export_presets.cfg','w',newline=chr(10)).write(cfg)
print('%d files in the build list'%len(keep))
