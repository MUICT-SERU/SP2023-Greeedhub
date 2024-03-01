import sys
keys=tuple(sys.modules.keys())
for key in keys:
    if "participation" in key or "percolation" in key:
        del sys.modules[key]
import participation as Pa, percolation as P
