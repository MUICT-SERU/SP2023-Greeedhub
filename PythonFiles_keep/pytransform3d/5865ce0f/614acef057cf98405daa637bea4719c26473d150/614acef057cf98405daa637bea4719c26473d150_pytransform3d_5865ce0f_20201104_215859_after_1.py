"""
========
Plot Box
========
"""
import numpy as np
import matplotlib.pyplot as plt
from pytransform3d.transformations import plot_transform
from pytransform3d.plot_utils import plot_box


random_state = np.random.RandomState(42)
ax = plot_box(size=[1, 1, 1], wireframe=False, alpha=0.1, color="k")
plot_box(ax=ax, size=[1, 1, 1], wireframe=True)
plot_transform(ax=ax, A2B=np.eye(4), s=0.3, lw=3)
plt.show()