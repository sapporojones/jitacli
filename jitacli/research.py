import re

a = "Republic Fleet Phased Plasma S x2400"
b = "Micro Auxiliary Power Core II"
c = "Gyrostabilizer II"

# r"[x]\d"

rea = re.search(r"[x]\d", a)
reb = re.search(r"[x]\d", b)
rec = re.search(r"[x]\d", c)

print(rea)
print(reb)
print(rec)

relist = []
relist.append(rea)
relist.append(reb)
relist.append(rec)

for item in relist:
    if item != None:
        print("found a match")
