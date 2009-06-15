import sys
import os
d = os.getcwd()[0]
sys.path.append(d+u":\\data\\python\\wpstats")
import wpstats

wpstats.WPStatsGUI().run()
