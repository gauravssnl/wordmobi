fi = open('wordmobi.mif','rb')
fo = open('icons.py','wt')

fo.write( "ICONS = '''")
while True:
    line = fi.read(40)
    if not line:
        break
    fo.write( "\n" )
    d = "".join([ "%02X" % ord(b) for b in line ])
    fo.write( d )

fo.write( "'''\n")
fo.close()
fi.close()
