import numpy as np

from linearmodels.panel.data import PanelData
from linearmodels.tests.panel._utility import generate_data

data = generate_data(0.00, 'pandas', ntk=(101, 5, 5), other_effects=1)

from linearmodels import PanelOLS
mod = PanelOLS(data.y, data.x, other_effects=data.c, weights=data.w)
mod.fit()

mod = PanelOLS(data.y, data.x, entity_effect=True, other_effects=data.c).fit()
mod = PanelOLS(data.y, data.x, entity_effect=True, other_effects=data.c).fit()
print(mod)
data = generate_data(0.00, 'pandas', ntk=(101, 5, 5), other_effects=2)
mod = PanelOLS(data.y, data.x, other_effects=data.c).fit()
# mod = PanelOLS(data.y, data.x, entity_effect=True, other_effects=data.c)
print(mod)