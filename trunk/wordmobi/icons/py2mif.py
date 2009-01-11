from icons import ICONS

fo = open('wordmobi2.mif','wb')

lines = ICONS.split("\n")
for line in lines:
    for p in range(0,len(line),2):
        b = int(line[p:p+2],16)
        fo.write( "%c" % chr(b) )
fo.close()

