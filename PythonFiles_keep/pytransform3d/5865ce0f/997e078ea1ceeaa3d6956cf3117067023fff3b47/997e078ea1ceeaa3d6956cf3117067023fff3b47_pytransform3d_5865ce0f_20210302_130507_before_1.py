"""
===================
Plot Transformation
===================

We can display transformations by plotting the basis vectors of the
corresponding coordinate frame.
"""
print(__doc__)


import matplotlib.pyplot as plt
from pytransform3d.transformations import plot_transform


plot_transform()
plt.show()
