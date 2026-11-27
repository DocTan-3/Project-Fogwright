# Building types: the one source for floorplans (wayfolk_plans.py), settlement plans (farhallow_plan.py) and, later,
# the 3D builder. A settlement plan may only place buildings defined here, so what is planned is what gets built.
#
# Coordinates in metres, the street along y = 0, x across the front. Each type has:
#   rooms   (x, y, w, h, label, kind)  the fixed part of the building, including its own yards
#   doors   (x, y, 'h'|'v', width, kind)  'd' door, 'g' gate or archway, 'o' open (no wall), 's' open shop front
#   hearths (x, y);  stairs (x, y, w, h, 'stairs'|'ladder');  windows (x, y, 'h'|'v', length)
#   plot    (x, w, min depth, max depth, label) or None: the plot behind the building (from the back of its rooms),
#           as deep as the ground allows on a real lot; plot_rooms/plot_doors show a typical full-depth plot
#   people  whose type it is ('wayfolk', or 'any' for plain sheds and the like)
#   doodads (x, y, w, h, kind, purpose): props that come with the building, in its coordinates (y < 0 is in front of
#           it, between the front and the street); plot_doodads the same with y measured from the start of the plot, and
#           only placed when the plot is that deep
T={}
def t(key,**k):
    k.setdefault('hearths',[]); k.setdefault('stairs',[]); k.setdefault('windows',[]); k.setdefault('plot',None)
    k.setdefault('plot_rooms',[]); k.setdefault('plot_doors',[]); k.setdefault('people','wayfolk'); k.setdefault('doodads',[]); k.setdefault('plot_doodads',[]); T[key]=k

t('street_house',name="Street house",size="6 × 10 m, 2-3 storeys, plot behind 4-16 m",
  rooms=[(0,0,4.6,5,'shop /\nworkshop','shop'),(4.6,0,1.4,10,'','room'),(0,5,4.6,5,'kitchen','room')],
  doors=[(5.3,0,'h',1,'d'),(4.6,2.5,'v',1,'d'),(4.6,7.6,'v',1,'d'),(5.3,10,'h',1,'d'),(2.4,10,'h',1,'d')],
  hearths=[(2.3,5)],stairs=[(0.1,5.6,1.1,2.6,'stairs')],windows=[(2.3,0,'h',3.2),(3.9,10,'h',1.0)],
  plot=(0,6,4,16,'yard and garden'),
  plot_rooms=[(0,10,6,7,'yard','yard'),(0,17,2.5,3,'store','out'),(2.5,17,1,3,'','yard'),(3.5,17,2.5,3,'privy,\nhens','out'),(0,20,6,6,'garden','garden')],
  plot_doors=[(1.25,17,'h',1,'d'),(4.75,17,'h',1,'d'),(3,17,'h',1,'o'),(3,20,'h',1,'o'),(3,26,'h',1,'g')],
  doodads=[(1.0,-0.6,1.6,0.5,'bench','sitting out by the shop in the evening'),(4.0,-0.5,0.6,0.3,'sign','the shop sign on its bracket')],
  plot_doodads=[(0.3,0.4,1.2,2.0,'woodpile','fuel for the kitchen hearth'),(3.5,1.0,2.0,0.2,'washing line','drying the wash'),(0.5,4.2,1.4,1.0,'hen coop','eggs')],
  note="street door into the side passage to the yard; the shop and kitchen open off it; stairs in the kitchen to the hall over the shop (jettied) and bedrooms behind; back-to-back hearth")
t('cottage',name="Cottage",size="6 × 8 m, one storey and a loft, yard behind 2-10 m",
  rooms=[(0,0,6,6,'main room','room'),(3.6,3.4,2.4,2.6,'bed\nalcove','room'),(0,6,6,2,'lean-to','out')],
  doors=[(1.6,0,'h',1,'d'),(3.6,4.7,'v',1.6,'o'),(5,8,'h',1,'d')],
  hearths=[(2.4,5.6)],stairs=[(0.2,4.2,0.8,1.6,'ladder')],windows=[(4.2,0,'h',1.4),(0,2.5,'v',1.2)],
  plot=(0,6,2,10,'yard and garden'),plot_rooms=[(0,8,6,6,'yard and garden','garden')],plot_doors=[(3,14,'h',1,'g')],
  doodads=[(3.2,-0.55,1.4,0.45,'bench','sitting out by the door, mending')],
  plot_doodads=[(0.3,0.3,1.0,1.8,'woodpile','fuel for the hearth'),(2.0,0.6,3.4,0.2,'washing line','drying the wash')],
  note="ladder to the loft over the back half; the lean-to opens to the yard; bench by the front door")
t('merchant_house',name="Merchant's house",size="14 × 16 m with coach yard and stable, walled garden 6-10 m",
  rooms=[(0,0,3.6,6,'counting\nroom','shop'),(3.6,0,2.8,6,'','room'),(6.4,0,3.6,6,'shop','shop'),(0,6,10,6,'kitchen and stores','room'),
         (10,0,4,12,'coach\nyard','yard'),(10,12,4,4,'stable','out')],
  doors=[(4.6,0,'h',1.2,'d'),(3.6,2,'v',1,'d'),(6.4,5.4,'v',0.9,'d'),(8.4,0,'h',1,'d'),(4.4,6,'h',1,'d'),(10,9,'v',1,'d'),
         (12,0,'h',2.6,'g'),(12,12,'h',1.6,'d'),(3,12,'h',1,'d')],
  hearths=[(0,9),(0,4.2)],stairs=[(5.2,1.0,1.1,3.2,'stairs')],windows=[(1.8,0,'h',1.4),(9.3,0,'h',1),(7,12,'h',2),(0,1.6,'v',1.2)],
  plot=(0,10,6,10,'walled garden'),plot_rooms=[(0,12,10,8,'walled garden','garden')],
  doodads=[(3.6,-0.5,0.4,0.4,'lamp','a brass lamp by the front door: the well-off light their doors')],
  plot_doodads=[(8.0,4.8,1.4,1.4,'well','their own well'),(1.0,1.0,3.0,1.2,'flower bed','a garden for show'),(6.5,1.2,2.2,2.2,'fruit tree','apples'),(1.0,4.6,1.8,0.5,'bench','sitting in the garden')],
  note="front door into the stair hall between counting room and shop; hall and parlour upstairs, bedrooms above; coach gate to the yard; own well in the garden")
t('merchant_house_small',name="Well-off house",size="10 × 12 m, 3 storeys, walled garden 6-10 m",
  rooms=[(0,0,3.6,6,'study','shop'),(3.6,0,2.8,6,'','room'),(6.4,0,3.6,6,'parlour','room'),(0,6,10,6,'kitchen and stores','room')],
  doors=[(4.6,0,'h',1.2,'d'),(3.6,2,'v',1,'d'),(6.4,5.4,'v',0.9,'d'),(4.4,6,'h',1,'d'),(3,12,'h',1,'d'),(10,9,'v',1,'d')],
  hearths=[(0,9),(0,4.2),(10,3)],stairs=[(5.2,1.0,1.1,3.2,'stairs')],windows=[(1.8,0,'h',1.4),(8.2,0,'h',1.4),(7,12,'h',2),(0,1.6,'v',1.2)],
  plot=(0,10,6,10,'walled garden'),plot_rooms=[(0,12,10,8,'walled garden','garden')],
  doodads=[(3.6,-0.5,0.4,0.4,'lamp','a brass lamp by the front door')],
  plot_doodads=[(8.0,4.8,1.4,1.4,'well','their own well'),(1.0,1.0,3.0,1.2,'flower bed','a garden for show'),(6.5,1.2,2.2,2.2,'fruit tree','pears'),(1.0,4.6,1.8,0.5,'bench','sitting in the garden')],
  note="the merchant's house without the coach yard: for the well-off who trade by ship or office, not by cart; a side door to the lane")
t('inn',name="Inn",size="12 × 16 m round a coach yard",
  rooms=[(0,0,7,6,'taproom\n(bar counter)','room'),(7,0,2,6,'arch-\nway','yard'),(9,0,3,6,'cellar\nstore','shop'),(0,6,4,6,'kitchen','room'),
         (4,6,8,6,'coach yard','yard'),(0,12,12,4,'stable','out')],
  doors=[(3.5,0,'h',1.2,'d'),(8,0,'h',2,'g'),(8,6,'h',2,'o'),(9,3,'v',1,'d'),(7,4.4,'v',1,'d'),(2,6,'h',1,'d'),(4,9,'v',1,'d'),
         (6,12,'h',1.6,'d'),(10,12,'h',1.6,'d')],
  hearths=[(0,3),(2,12)],stairs=[(5,0.3,1.8,2.2,'stairs'),(10.2,6.2,1.6,2.6,'stairs')],windows=[(1.6,0,'h',1.6),(10.5,0,'h',1),(0,8.5,'v',1)],
  doodads=[(0.3,-0.6,1.8,0.5,'bench','drinkers sitting out front'),(4.6,-0.4,0.6,0.3,'sign','the Gull & Lantern sign on its bracket'),(2.6,-0.4,0.4,0.4,'lamp','the lantern by the inn door'),
         (4.6,10.4,2.2,0.7,'trough','water for horses in the coach yard'),(9.6,6.6,1.0,1.0,'barrel','ale barrels by the cellar')],
  note="stairs from the taproom and from the yard gallery up to the guest rooms; the archway takes coaches to the yard and stable")
t('waylodge',name="Waylodge",size="8 × 12 m, beside the waystone",
  rooms=[(0,0,8,8,'common room\nbenches, long table','room'),(0,8,8,2,'bunks','room'),(0,10,4,2,"priest",'room'),(4,10,4,2,'store','out')],
  doors=[(4,0,'h',1.2,'d'),(4,8,'h',2,'o'),(2,10,'h',1,'d'),(6,10,'h',1,'d'),(8,11,'v',1,'d')],
  hearths=[(8,4)],stairs=[(7,8.1,0.8,1.8,'ladder')],windows=[(1.6,0,'h',1.4),(6.4,0,'h',1.4),(0,4,'v',1.6)],
  note="ladder to the sleeping lofts over the bunks; the road lamp burns all night over the street door; store door to the back")
t('waystone',name="Waystone shrine",size="5 × 5 m: stone 2.5 m tall on a stepped base",
  rooms=[(0,0,5,5,'','stone')],doors=[(2.5,0,'h',3,'o')],
  note="carved with the roads and their distances; the lamp niche faces the main road; in towns under an open roof on four posts")
t('waystone_village',name="Village waystone",size="3 × 3 m: stone 2 m tall on one step",
  rooms=[(0,0,3,3,'','stone')],doors=[(1.5,0,'h',2,'o')],
  note="an old, plain stone with the roads and distances worn faint; lamp niche facing the main road")
t('workshop',name="Workshop with yard",size="10 × 10 m (smithy, cooper, carpenter)",
  rooms=[(0,0,6,5,'open work bay:\nforge or bench','shop'),(0,5,6,5,'store','room'),(6,0,4,10,'yard: fuel,\nmaterials','yard')],
  doors=[(3,0,'h',4.4,'s'),(6,2.5,'v',1,'d'),(3,5,'h',1,'d'),(6,7.5,'v',1,'d'),(8,0,'h',2.4,'g')],
  hearths=[(0,1.2)],windows=[(0,7.5,'v',1.2)],
  doodads=[(3.0,2.0,1.0,0.6,'anvil','the smith works here'),(4.3,3.8,1.6,0.6,'quench trough','quenching hot iron'),(0.6,3.6,0.8,0.8,'grindstone','sharpening'),
              (6.6,1.0,1.8,1.8,'charcoal','fuel for the forge'),(8.2,5.0,1.3,3.4,'woodpile','firewood for the forge'),(6.6,8.6,0.6,0.6,'chopping block','the hatchet in the block: the first weapon (beat B)')],
  note="the whole front of the work bay opens to the street by day, shuttered at night; smoky trades at the downwind end of town")
t('farmstead',name="Farmstead",size="12 × 12 m: house, byre and barn round a yard",
  rooms=[(0,0,4,8,'house','room'),(4,0,4,8,'yard','yard'),(8,0,4,8,'byre','out'),(0,8,12,4,'barn','out')],
  doors=[(6,0,'h',2.4,'g'),(4,4,'v',1,'d'),(8,4,'v',1.6,'d'),(6,8,'h',2.4,'d')],
  hearths=[(0,5)],stairs=[(0.2,0.3,0.8,1.6,'ladder')],windows=[(2,0,'h',1.4),(0,2.5,'v',1)],
  doodads=[(4.3,2.0,1.4,2.6,'cart','the farm cart'),(6.6,6.6,1.0,1.0,'manure heap','for the fields'),(6.4,2.4,1.2,0.6,'trough','water for the beasts')],
  note="all doors face the yard; the yard gate faces the road; ladder to the loft")
# plain buildings any people might put up
t('store',people='any',name="Store or salt house",size="8 × 6 m, one room",
  rooms=[(0,0,8,6,'store','out')],doors=[(4,0,'h',2.4,'d')],windows=[(0,3,'v',0.8)],
  doodads=[(0.3,-0.75,0.8,0.7,'barrel','salt fish barrels waiting for the ship'),(1.3,-0.75,0.8,0.7,'barrel','salt fish barrels')],
  note="wide double doors for barrels and carts; small high windows")
t('smokehouse',people='any',name="Smokehouse",size="6 × 6 m",
  rooms=[(0,0,6,4,'smoke room\n(racks)','out'),(0,4,6,2,'fire pit','out')],doors=[(3,0,'h',1,'d'),(3,4,'h',1.2,'o')],
  hearths=[(3,5)],doodads=[(0.2,-0.9,1.6,0.6,'woodpile','oak and alder for the smoke')],
  note="the fire is fed from below; fish hang on racks up into the roof; louvres under the ridge")
t('boat_shed',people='any',name="Boatwright's shed",size="8 × 6 m, open to the shore",
  rooms=[(0,0,8,6,'slipway\nand bench','out')],doors=[(4,0,'h',6,'s')],
  doodads=[(0.3,3.8,1.6,1.6,'boat hull','a hull on trestles, half built')],
  note="open along the front for hulls; tools along the back wall; a slipway down to the water")
t('salt_works',people='any',name="Salt-boiling hut",size="6 × 9 m with its pans",
  rooms=[(0,0,6,5,'boiling hut','out'),(0,5,6,4,'salt pans','yard')],doors=[(3,0,'h',1.2,'d'),(3,5,'h',1.2,'d')],
  hearths=[(3,2.6)],doodads=[(0.2,-0.9,1.6,0.6,'woodpile','driftwood for the pans'),(4.8,-0.7,1.0,0.6,'sacks','salt in sacks')],
  note="seawater boiled down in iron pans over a driftwood fire; the drying pans outside face the sea")
t('granary',people='any',name="Granary",size="8 × 6 m on staddle stones",
  rooms=[(0,0,8,6,'grain bins','out')],doors=[(4,0,'h',1.4,'d')],
  doodads=[(0.3,-0.75,2.2,0.7,'sacks','grain going in at harvest'),(6.0,-0.75,0.7,0.7,'barrel','water barrel in case of fire')],
  note="raised on mushroom-shaped stones against rats; loose wooden steps up to the door, outside, taken away at night")
t('guard_post',people='any',name="Guard post",size="4 × 4 m with the bell frame",
  rooms=[(0,0,4,4,'guard\nroom','room')],doors=[(2,0,'h',1,'d')],hearths=[(4,2)],windows=[(0,2,'v',0.8)],
  doodads=[(4.3,0.4,1.2,1.4,'bell frame','the alarm bell (rung in beat 2)')],
  note="the alarm bell hangs in a frame beside it (rung in beat 2)")
t('hen_house',people='any',name="Hen house and goat pen",size="4 × 7 m",
  rooms=[(0,0,4,3,'hen house','out'),(0,3,4,4,'goat pen','yard')],doors=[(2,0,'h',1,'d'),(2,3,'h',1,'o')],
  doodads=[(0.4,4.0,1.2,0.5,'trough','water for the goats')],
  note="a pop-hole for the hens; the pen fenced with wattle")
t('merrith_shrine',people='any',name="Shrine of Merrith",size="5 × 5 m",
  rooms=[(0,0,5,5,'altar','room')],doors=[(2.5,0,'h',1.2,'d')],windows=[(0,2.5,'v',1),(5,2.5,'v',1)],
  doodads=[(0.1,-0.9,1.2,0.45,'bench','a stone bench for the shrine keeper and mourners'),(3.4,-0.6,0.5,0.5,'candles','candles and offerings at the door')],
  note="Farhallow's small shrine to the merciful goddess: candles, offerings, a stone bench by the door")

def footprint(k):   # the fixed part's width (along the street) and depth
    r=T[k]['rooms']; return max(a[0]+a[2] for a in r),max(a[1]+a[3] for a in r)

def export(path):   # for the game: godot/data/building_types.json
    import json
    json.dump(T,open(path,'w'),indent=1)
if __name__=='__main__':
    import sys,os
    export(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','godot','data','building_types.json'))
