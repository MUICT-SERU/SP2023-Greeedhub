import os, percolation as P
from percolation.rdf import NS
PERCOLATIONROOT=os.path.expanduser("~/.percolation/")
PARTICIPATIONDIR=PERCOLATIONROOT+"participation/"
if not os.path.isdir(PERCOLATIONROOT):
    os.mkdir(PERCOLATIONROOT)
if not os.path.isdir(PARTICIPATIONDIR):
    os.mkdir(PARTICIPATIONDIR)
RENDERDIR=PARTICIPATIONDIR+"rdf/"
PACKAGEDIR=os.path.dirname(__file__)
DATADIR=PACKAGEDIR+"/../data/"
P.start(start_session=False)
P.percolation_graph.bind("po",NS.po)
