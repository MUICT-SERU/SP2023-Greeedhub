import sys
keys=tuple(sys.modules.keys())
for key in keys:
    if "participation" in key or "percolation" in key:
        del sys.modules[key]
import participation as Pa, percolation as P
from percolation.rdf import NS, a, po, c

#ss=Pa.aa.access.parseLegacyFiles()
#ss=Pa.aa.access.parseLegacyFiles(1,0,0,0)
#ss=Pa.aa.access.parseLegacyFiles(0,1,0,0)
ss=Pa.aa.access.parseLegacyFiles(0,0,1,0)

triplification_classes=Pa.aa.render.publishAll(*ss)
c("finished publication of all")
