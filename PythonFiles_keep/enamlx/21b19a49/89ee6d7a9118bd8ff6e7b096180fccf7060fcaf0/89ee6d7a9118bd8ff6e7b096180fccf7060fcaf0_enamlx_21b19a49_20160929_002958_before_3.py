'''
Created on Sep 28, 2016

@author: 
'''
from enaml.qt.qt_factories import QT_FACTORIES

def occ_box_factory():
    from occ.occ_brep import OccBox
    return OccBox

def occ_cone_factory():
    from occ.occ_brep import OccCone
    return OccCone

def occ_cylinder_factory():
    from occ.occ_brep import OccCylinder
    return OccCylinder

def occ_half_space_factory():
    from occ.occ_brep import OccHalfSpace
    return OccHalfSpace

def occ_one_axis_factory():
    from occ.occ_brep import OccOneAxis
    return OccOneAxis

def occ_prism_factory():
    from occ.occ_brep import OccPrism
    return OccPrism

def occ_revol_factory():
    from occ.occ_brep import OccRevol
    return OccRevol

def occ_revolution_factory():
    from occ.occ_brep import OccRevolution
    return OccRevolution

def occ_sphere_factory():
    from occ.occ_brep import OccSphere
    return OccSphere

def occ_sweep_factory():
    from occ.occ_brep import OccSweep
    return OccSweep

def occ_torus_factory():
    from occ.occ_brep import OccTorus
    return OccTorus

def occ_wedge_factory():
    from occ.occ_brep import OccWedge
    return OccWedge

QT_FACTORIES['Box'] = occ_box_factory
QT_FACTORIES['Cone'] = occ_cone_factory
QT_FACTORIES['Cylinder'] = occ_cylinder_factory
QT_FACTORIES['HalfSpace'] = occ_half_space_factory
#QT_FACTORIES['OneAxis'] = occ_one_axis_factory
QT_FACTORIES['Prism'] = occ_prism_factory
QT_FACTORIES['Revol'] = occ_revol_factory
QT_FACTORIES['Revolution'] = occ_revolution_factory
QT_FACTORIES['Sphere'] = occ_sphere_factory
QT_FACTORIES['Sweep'] = occ_sweep_factory
QT_FACTORIES['Torus'] = occ_torus_factory
QT_FACTORIES['Wedge'] = occ_wedge_factory
