import ReSTed
import os
import sys
path = sys.argv[0]
webRoot = path[0:path.rfind(os.sep)+1]
ReSTed.start(sys.argv[1],webRoot)