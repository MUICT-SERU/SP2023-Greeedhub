import sys
keys = tuple(sys.modules.keys())
for key in keys:
    if "participation" in key or "percolation" in key:
        del sys.modules[key]
import participation as Pa
from percolation.rdf import c

# ss=Pa.aa.access.parseLegacyFiles()
# ss=Pa.aa.access.parseLegacyFiles(1,0,0,0)
# ss=Pa.aa.access.parseLegacyFiles(0,1,0,0)
# ss=Pa.aa.access.parseLegacyFiles(0,0,1,0)
#
# triplification_classes=Pa.aa.render.publishAll(*ss)
# c("finished publication of all aa")

triplification_class = Pa.participabr.access.parseLegacyFiles()
# triplification_class = Pa.participabr.access.parseLegacyFiles(profiles=False)
# triplification_class = Pa.participabr.access.parseLegacyFiles(profiles=False,
#                                                             articles=False,
#                                                             comments=False)
c("finished publication of participabr")
