# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np


class Memorize(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        if self.keys():
            m = max(map(len, list(self.keys()))) + 1
            return '\n'.join([k.rjust(m) + ': ' + repr(v)
                              for k, v in sorted(self.items())])
        else:
            return self.__class__.__name__ + "()"

    def __dir__(self):
        return list(self.keys())


class ReflectanceResult(dict):
    """ Represents the reflectance result.

    Returns
    -------
    All returns are attributes!
    BSC.ref, BSC.refdB : array_like
        Radar Backscatter values (polarization-independent).
    BSC.VV, BSC.HH, BSC.VVdB, BSC.HHdB, BSC.array, BSC,arraydB : array_like
        Radar Backscatter values (polarization-dependent). BSC.array contains the results as an array like array([BSC.VV, BSC.HH]).
    BRDF.ref, BRDF.refdB : array_like
        BRDF reflectance values (polarization-independent).
    BRDF.VV, BRDF.HH, BRDF.VVdB, BRDF.HHdB, BRDF.array, BRDF,arraydB : array_like
        BRDF reflectance values (polarization-dependent). BRDF.array contains the results as an array like array([BRDF.VV, BRDF.HH]).
    BRF.ref, BRF.refdB : array_like
        BRF reflectance values (polarization-independent).
    BRF.VV, BRF.HH, BRF.VVdB, BRF.HHdB, BRF.array, BRF,arraydB : array_like
        BRF reflectance values (polarization-dependent). BRF.array contains the results as an array like array([BRF.VV, BRF.HH]).

    Notes
    -----
    There may be additional attributes not listed above depending of the
    specific solver. Since this class is essentially a subclass of dict
    with attribute accessors, one can see which attributes are available
    using the `keys()` method. adar Backscatter values of multi scattering contribution of surface and volume

    The attribute 'ms' is the multi scattering contribution. This is only available if it is calculated. For detailed
    parametrisation one can use BSC.ms.sms or BSC.ms.smv for the multiple scattering contribution of surface or volume,
    respectively.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        if self.keys():
            m = max(map(len, list(self.keys()))) + 1
            return '\n'.join([k.rjust(m) + ': ' + repr(v)
                              for k, v in sorted(self.items())])
        else:
            return self.__class__.__name__ + "()"

    def __dir__(self):
        return list(self.keys())


class SailResult(dict):
    """ Represents the sail result.

    Returns
    -------
    All returns are attributes!
    SDR.ref, SDR.refdB : array_like
        Directional reflectance factor.
    BHR.ref, BHR.refdB : array_like
        Bi-hemispherical reflectance factor.
    DHR.ref, DHR.refdB : array_like
        Directional-Hemispherical reflectance factor.
    HDR.ref, HDR.refdB : array_like
        Hemispherical-Directional reflectance factor.

    Note
    ----
    All returns have in addition the attributes `L8.Bx` and `ASTER.Bx`. L8 is the Landsat 8 average reflectance values
    for Bx band (B2 until B7). `ASTER` is the ASTER average reflectance for Bx band (B1 until B9).

    Notes
    -----
    There may be additional attributes not listed above depending of the
    specific solver. Since this class is essentially a subclass of dict
    with attribute accessors, one can see which attributes are available
    using the `keys()` method. adar Backscatter values of multi scattering contribution of surface and volume

    The attribute 'ms' is the multi scattering contribution. This is only available if it is calculated. For detailed
    parametrisation one can use BSC.ms.sms or BSC.ms.smv for the multiple scattering contribution of surface or volume,
    respectively.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        if self.keys():
            m = max(map(len, list(self.keys()))) + 1
            return '\n'.join([k.rjust(m) + ': ' + repr(v)
                              for k, v in sorted(self.items())])
        else:
            return self.__class__.__name__ + "()"

    def __dir__(self):
        return list(self.keys())


class EmissivityResult(dict):
    """ Represents the reflectance result.

    Returns
    -------
    All returns are attributes!
    EMN.VV, EMN.HH, EMN.VVdB, EMN.HHdB, EMN.array, EMN,arraydB : array_like : array_like
        Normalized Emission values (use EMS for emission values). Due to the several conversions in some other models
        this output format delivers the emission values divided through the
        sensing geometry times 4pi. This attribute is only for the I2EM.Emissivity class. If you want to calculate the
        emissivity of a scene, use this output from EMS.
        EMN.array contains the results as an array like array([EMN.VV, EMN.HH]).
    EMS.VV, EMS.HH, EMS.VVdB, EMS.HHdB, EMN.array, EMN,arraydB : array_like
        Emission values. EMS.array contains the results as an array like array([EMS.VV, EMS.HH]).

    Notes
    -----
    There may be additional attributes not listed above depending of the
    specific solver. Since this class is essentially a subclass of dict
    with attribute accessors, one can see which attributes are available
    using the `keys()` method. adar Backscatter values of multi scattering contribution of surface and volume

    The attribute 'ms' is the multi scattering contribution. This is only available if it is calculated. For detailed
    parametrisation one can use BSC.ms.sms or BSC.ms.smv for the multiple scattering contribution of surface or volume,
    respectively.
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        if self.keys():
            m = max(map(len, list(self.keys()))) + 1
            return '\n'.join([k.rjust(m) + ': ' + repr(v)
                              for k, v in sorted(self.items())])
        else:
            return self.__class__.__name__ + "()"

    def __dir__(self):
        return list(self.keys())


def rad(angle):
    """
    Convert degrees to radians.

    Parameter:
    ----------
    angle : (int, float or array_like)
        Angle in [DEG].
    """

    return angle * np.pi / 180.0


def deg(angle):
    """
    Convert radians to degree.

    Parameter:
    ----------
    angle : (int, float or array_like)
        Angle in [RAD].
    """

    return angle * 180. / np.pi


def sec(angle):
    """
    Secant of an angle.
    """
    return 1 / np.cos(angle)


def cot(x):
    """
    Cotangent of an angle.
    """
    return 1 / np.tan(x)


def dB(x):
    """
    Convert a linear value to dB.
    """
    with np.errstate(invalid='ignore'):
        return 10 * np.log10(x)


def linear(x):
    """
    Convert a dB value in linear.
    """
    return 10 ** (x / 10)


def BRDF(BSC, iza, vza, angle_unit='RAD'):
    """
    Convert a Radar Backscatter Coefficient (BSC) into a BRDF.

    Note
    -----
    Hot spot direction is vza == iza and raa = 0.0

    Parameters
    ----------
    BSC : int, float or array_like
        Radar Backscatter Coefficient (sigma 0).

    iza : int, float or array_like
        Sun or incidence zenith angle.

    vza : int, float or array_like
        View or scattering zenith angle.

    angle_unit : {'DEG', 'RAD'} (default = 'RAD'), optional
        * 'DEG': All input angles (iza, vza, raa) are in [DEG].
        * 'RAD': All input angles (iza, vza, raa) are in [RAD].

    Returns
    -------
    BRDF value : int, float or array_like

    """
    if angle_unit == 'RAD':
        return BSC / (np.cos(iza) * np.cos(vza) * (4 * np.pi))

    elif angle_unit == 'DEG':
        return BSC / (np.cos(rad(iza)) * np.cos(rad(vza)) * (4 * np.pi))
    else:
        raise ValueError("angle_unit must be 'RAD' or 'DEG'")


def BRF(BRDF):
    """
    Convert a BRDF into a BRF.

    Note
    -----
    Hot spot direction is vza == iza and raa = 0.0

    Parameters
    ----------
    BRDF : int, float or array_like
        BRDF value.

    Returns
    -------
    BRF value : int, float or array_like

    """
    return np.pi * BRDF


def BSC(BRDF, iza, vza, angle_unit='RAD'):
    """
    Convert a BRDF in to a Radar Backscatter Coefficient (BSC).

    Note
    -----
    Hot spot direction is vza == iza and raa = 0.0

    Parameters
    ----------
    BSC : int, float or array_like
        Radar Backscatter Coefficient (sigma 0).

    iza : int, float or array_like
        Sun or incidence zenith angle.

    vza : int, float or array_like
        View or scattering zenith angle.

    angle_unit : {'DEG', 'RAD'} (default = 'RAD'), optional
        * 'DEG': All input angles (iza, vza, raa) are in [DEG].
        * 'RAD': All input angles (iza, vza, raa) are in [RAD].

    Returns
    -------
    BRDF value : int, float or array_like

    """
    if angle_unit == 'RAD':
        return BRDF * np.cos(iza) * np.cos(vza) * 4 * np.pi

    elif angle_unit == 'DEG':
        return BRDF * np.cos(rad(iza)) * np.cos(rad(vza)) * (4 * np.pi)
    else:
        raise ValueError("angle_unit must be 'RAD' or 'DEG'")


def align_all(data, constant_values='default'):
    max_len = max_length(data)

    if constant_values == 'default':
        return np.asarray(
            [np.pad(item, (0, max_len - len(item)), 'constant', constant_values=item[-1]) for item in data])
    else:
        return np.asarray(
            [np.pad(item, (0, max_len - len(item)), 'constant', constant_values=constant_values) for item in data])


def max_length(data):
    return np.max([len(item) for item in data])


def asarrays(data):
    return [np.asarray(item).flatten() for item in data]


def load_param():
    sensing = Memorize(freq=1.26,
                       iza=35,
                       vza=30,
                       raa=50)

    # W1
    W1 = Memorize(hs=0.3,
                  l=30,
                  S=0.8,
                  C=0.15,
                  mv=0.2,
                  pb=1.7,
                  p0=0.31831,
                  N=1,
                  Cab=20,
                  Cxc=3,
                  Cb=0.4,
                  Cw=0.0005,
                  Cm=0.0085,
                  LAI=1,
                  lza=45,
                  zmax=30,
                  bsp=15,
                  h=15,
                  r=3,
                  hb=1,
                  bspr=5,
                  mg=0.19,
                  T0=16,
                  a=0.02)

    W2 = Memorize(hs=0.55,
                  l=28,
                  S=0.8,
                  C=0.15,
                  mv=0.35,
                  pb=1.7,
                  p0=0.31831,
                  N=1.5,
                  Cab=35,
                  Cxc=5,
                  Cb=0.15,
                  Cw=0.003,
                  Cm=0.0055,
                  LAI=4,
                  lza=45,
                  zmax=30,
                  bsp=15,
                  h=15,
                  r=3,
                  hb=1,
                  bspr=5,
                  mg=0.28,
                  T0=20,
                  a=0.02)

    W3 = Memorize(hs=0.60,
                  l=25,
                  S=0.8,
                  C=0.15,
                  mv=0.45,
                  pb=1.7,
                  p0=0.31831,
                  N=2.2,
                  Cab=47,
                  Cxc=9,
                  Cb=0,
                  Cw=0.005,
                  Cm=0.002,
                  LAI=7,
                  lza=45,
                  zmax=30,
                  bsp=15,
                  h=15,
                  r=3,
                  hb=1,
                  bspr=5,
                  mg=0.51,
                  T0=24,
                  a=0.02)

    return Memorize(sensing=sensing,
                    W1=W1,
                    W2=W2,
                    W3=W3)
