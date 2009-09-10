import os

locs = [ __import__(f[:f.find('.')]) for f in os.listdir('.')
         if f.endswith('.py') and f.startswith('wm') ]

for loc in locs:
    print "-"*60
    print "Locales for", loc.__name__
    print "-"*60
    for strs in dir(loc):
        if strs not in [ '__builtins__', '__doc__', '__file__', '__name__' ]:
            print strs, "=>", getattr(loc,strs)
    
    
    
