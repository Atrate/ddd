# Jose Juan Montes 2019-2020

from ddd.pack.sketchy import urban, landscape, industrial, plants
from ddd.ddd import ddd
import math

items = ddd.group3()

heights = (3.0, 5.0, 10.0, 15.0)

for h in heights:
    item = plants.reed(height=h)
    items.append(item)

for h in heights:
    item = plants.tree_default(height=h)
    items.append(item)

for h in heights:
    item = plants.tree_palm(height=h)
    items.append(item)

for h in heights:
    item = plants.tree_fir(height=h)
    items.append(item)

items = ddd.align.grid(items)
items.append(ddd.helper.all())
items.show()

items.save("/tmp/test.glb")
items.save("/tmp/test.json"

           )
