from __future__ import print_function, absolute_import, division

from numpy import (ceil, where, argsort, r_, unique, zeros, arange, pi, sin,
                   cos, empty, sum)
from numpy.linalg import pinv, inv


def kernel_weight_bartlett(max_lag):
    """
    Kernel weights from a Bartlett kernel

    Parameters
    ----------
    max_lag : int
       Maximum lag to used in kernel

    Returns
    -------
    weights : ndarray
        Weight array  ordered by lag position (maxlag + 1)

    Notes
    -----
    .. math::

       w_i = 1 - i / (m + 1), \, i < m
    """
    return 1 - arange(max_lag + 1) / (max_lag + 1)


def kernel_weight_quadratic_spectral(max_lag):
    r"""
    Kernel weights from a quadratic-spectral kernel

    Parameters
    ----------
    max_lag : int
       Maximum lag to used in kernel

    Returns
    -------
    weights : ndarray
        Weight array  ordered by lag position (maxlag + 1)

    Notes
    -----
    .. math::

       z_i & = 6i\pi / 5                                        \\
       w_0 &  = 1                                                \\
       w_i &  = 3(\sin(z_i)/z_i - cos(z_i))/z_i^ 2, \, i \geq 1
    """
    w = 6 * pi * arange(max_lag + 1) / 5
    w[0] = 1
    w[1:] = 3 * (sin(w[1:]) / w[1:] - cos(w[1:])) / w[1:] ** 2
    return w


def kernel_weight_parzen(max_lag):
    r"""
    Kernel weights from a Parzen kernel

    Parameters
    ----------
    max_lag : int
       Maximum lag to used in kernel

    Returns
    -------
    weights : ndarray
        Weight array  ordered by lag position (maxlag + 1)

    Notes
    -----
    .. math::

       z_i & = i / (m+1)                    \\
       w_i &  = 1-6z_i^2+6z_i^3, z \leq 0.5 \\
       w_i &  = 2(1-z_i)^3, z > 0.5
    """
    z = arange(max_lag + 1) / (max_lag + 1)
    w = 1 - 6 * z ** 2 + 6 * z ** 3
    w[z > 0.5] = 2 * (1 - z[z > 0.5]) ** 3
    return w


def kernel_optimal_bandwidth(x, kernel='bartlett'):
    """
    Parameters
    x : ndarray
        Array of data to use when computing optimal bandwidth
    kernel : str, optional
        Name of kernel to use.  Supported kernels include:
        
          * 'bartlett', 'newey-west' : Bartlett's kernel
          * 'parzen', 'gallane' : Parzen's kernel
          * 'qs', 'quadratic-spectral', 'andrews : Quadratic spectral kernel
    
    Returns
    -------
    m : int
        Optimal bandwidth. Set to nobs - 1 if computed bandwidth is larger.
    
    Notes
    -----
    
    .. todo::
    
      * Explain mathematics involved
      * References
    """
    t = x.shape[0]
    x = x.squeeze()
    if kernel in ('bartlett', 'newey-west'):
        q, c = 1, 1.1447
        m_star = int(ceil(4 * (t / 100) ** (2 / 9)))
    elif kernel in ('qs', 'andrews', 'quadratic-spectral'):
        q, c = 2, 1.3221
        m_star = int(ceil(4 * (t / 100) ** (4 / 25)))
    elif kernel in ('gallant', 'parzen'):
        q, c = 2, 2.6614
        m_star = int(ceil(4 * (t / 100) ** (2 / 25)))
    else:
        raise ValueError('Unknown kernel: {0}'.format(kernel))
    sigma = empty(m_star + 1)
    sigma[0] = x.T @ x / t
    for i in range(1, m_star + 1):
        sigma[i] = x[i:].T @ x[:-i] / t
    s0 = sigma[0] + 2 * sigma[1:].sum()
    sq = 2 * sum(sigma[1:] * arange(1, m_star + 1) ** q)
    rate = 1 / (2 * q + 1)
    gamma = c * ((sq / s0) ** 2) ** rate
    m = gamma * t ** rate
    return min(int(ceil(m)), t - 1)


KERNEL_LOOKUP = {'bartlett': kernel_weight_bartlett,
                 'newey-west': kernel_weight_bartlett,
                 'quadratic-spectral': kernel_weight_quadratic_spectral,
                 'qs': kernel_weight_quadratic_spectral,
                 'andrews': kernel_weight_quadratic_spectral,
                 'gallant': kernel_weight_parzen,
                 'parzen': kernel_weight_parzen}


class HomoskedasticCovariance(object):
    r"""
    Covariance estimation for homoskedastic data
    
    Parameters
    ----------
    x : ndarray
        Model regressors (nobs by nvar)
    y : ndarray
        Series modeled (nobs by 1)
    z : ndarray
        Instruments used for endogenous regressors (nobs by ninstr)
    params : ndarray
        Estimated model parameters (nvar by 1)
    debiased : bool, optional
        Flag indicating whether to use a small-sample adjustment
    
    Notes
    -----
    Covariance is estimated using 
    
    .. math ::
    
        n^{-1} s^2 V^{-1}   
    
    where 
    
    .. math:: 
    
      s^2 = n^{-1} \sum_{i=1}^n \hat{\epsilon}_i^2
    
    If ``debiased`` is true, then :math:`s^2` is scaled by n / (n-k).
    
    .. math:: 
    
      V = n^{-1} X'Z(Z'Z)^{-1}Z'X
    
    where :math:`X` is the matrix of variables included in the model and 
    :math:`Z` is the matrix of instruments, including exogenous regressors.
    """

    def __init__(self, x, y, z, params, debiased=False):
        self.x = x
        self.y = y
        self.z = z
        self.params = params
        self._debiased = debiased
        self.eps = y - x @ params
        self._pinvz = pinv(z)

    @property
    def s(self):
        """Score covariance estimate"""
        x, z, eps = self.x, self.z, self.eps
        nobs, nvar = x.shape
        s2 = eps.T @ eps / nobs
        pinvz = self._pinvz
        v = (x.T @ z) @ (pinvz @ x) / nobs

        return s2 * v

    @property
    def cov(self):
        """Covariance of estimated parameters"""

        x, z = self.x, self.z
        nobs, nvar = x.shape

        scale = nobs / (nobs - nvar) if self._debiased else 1
        pinvz = self._pinvz
        v = (x.T @ z) @ (pinvz @ x) / nobs
        vinv = inv(v)

        return scale * vinv @ self.s @ vinv / nobs

    @property
    def s2(self):
        """
        Estimated variance of residuals. Small-sample adjusted if debiased.
        """
        nobs, nvar = self.x.shape
        eps = self.eps
        denom = nobs - nvar if self.debiased else nobs

        return eps.T @ eps / denom

    @property
    def debiased(self):
        """Flag indicating whether to debias"""
        return self._debiased

    @property
    def config(self):
        return {'debiased': self.debiased,
                'name': self.__class__.__name__}


class HeteroskedasticCovariance(HomoskedasticCovariance):
    """
    Covariance estimation for heteroskedastic data

    Parameters
    ----------
    x : ndarray
        Model regressors (nobs by nvar)
    y : ndarray
        Series ,modeled (nobs by 1)
    z : ndarray
        Instruments used for endogensou regressors (nobs by ninstr)
    params : ndarray
        Estimated model parameters (nvar by 1)
    debiased : bool, optional
        Flag indicating whether to use a small-sample adjustment

    Notes
    -----
    Covariance is estimated using 

    .. math ::

        n^{-1} V^{-1} \hat{S} V^{-1}  

    where 

    .. math:: 

      \hat{S} = n^{-1} \sum_{i=1}^n \hat{\epsilon}_i^2 \hat{x}_i^{\prime} \hat{x}_i

    where :math:`\hat{\gamma}=(Z'Z)^{-1}(Z'X)` and 
    :math:`\hat{x}_i = z_i\hat{\gamma}`. If ``debiased`` is true, then 
    :math:`S` is scaled by n / (n-k).

    .. math:: 

      V = n^{-1} X'Z(Z'Z)^{-1}Z'X

    where :math:`X` is the matrix of variables included in the model and 
    :math:`Z` is the matrix of instruments, including exogenous regressors.
    """

    def __init__(self, x, y, z, params, debiased=False):
        super(HeteroskedasticCovariance, self).__init__(x, y, z, params, debiased)

    @property
    def s(self):
        """Heteroskedasticity-robust score covariance estimate"""
        x, z, eps = self.x, self.z, self.eps
        nobs, nvar = x.shape
        pinvz = self._pinvz
        xhat_e = z @ (pinvz @ x) * eps
        s = xhat_e.T @ xhat_e / nobs
        return s


class KernelCovariance(HomoskedasticCovariance):
    r"""
    Kernel weighted (HAC) covariance estimation

    Parameters
    ----------
    x : ndarray
        Model regressors (nobs by nvar)
    y : ndarray
        Series ,modeled (nobs by 1)
    z : ndarray
        Instruments used for endogensou regressors (nobs by ninstr)
    params : ndarray
        Estimated model parameters (nvar by 1)
    debiased : bool, optional
        Flag indicating whether to use a small-sample adjustment
    kernel : str
        Kernel name. Supported kernels are: 

        * 'bartlett', 'newey-west' - Triangular kernel 
        * 'qs', 'quadratic-spectral', 'andrews' - Quadratic spectral kernel
        * 'parzen', 'gallant' - Parzen's kernel;
          
    bandwidth : {int, None}
        Non-negative bandwidth to use with kernel. If None, automatic
        bandwidth selection is used.

    Notes
    -----
    Covariance is estimated using 
    
    .. math ::
    
        n^{-1} V^{-1} \hat{S} V^{-1}  
    
    where 
    
    .. math:: 
    
      \hat{S}_0 & = n^{-1} \sum_{i=1}^{n} \hat{\epsilon}^2_i \hat{x}_i^{\prime}
           \hat{x}_{i} \\
      \hat{S}_j & = n^{-1} \sum_{i=1}^{n-j} 
          \hat{\epsilon}_i\hat{\epsilon}_{i+j} (\hat{x}_i^{\prime} 
          \hat{x}_{i+j} + \hat{x}_{i+j}^{\prime} \hat{x}_{i}) \\
      \hat{S}   & = \sum_{i=0}^{bw} K(i, bw) \hat{S}_i 
    
    where :math:`\hat{\gamma}=(Z'Z)^{-1}(Z'X)`,  
    :math:`\hat{x}_i = z_i\hat{\gamma}` and :math:`K(i,bw)` is a weight that 
    depends on the kernel. If ``debiased`` is true, then :math:`S` is scaled 
    by n / (n-k).
    
    .. math:: 
    
      V = n^{-1} X'Z(Z'Z)^{-1}Z'X
    
    where :math:`X` is the matrix of variables included in the model and 
    :math:`Z` is the matrix of instruments, including exogenous regressors.
    """

    def __init__(self, x, y, z, params, debiased=False, kernel='bartlett',
                 bandwidth=None):
        super(KernelCovariance, self).__init__(x, y, z, params, debiased)
        self._kernel = kernel
        self._bandwidth = bandwidth
        self._kernels = KERNEL_LOOKUP

    @property
    def s(self):
        """HAC score covariance estimate"""
        x, z, eps = self.x, self.z, self.eps
        nobs, nvar = x.shape

        kernel = self.config['kernel']
        # TODO: Bandwidth selection method
        bw = self.config['bw']
        if bw is None:
            if kernel in ('newey-west', 'bartlett'):
                bw = ceil(20 * (nobs / 100) ** (2 / 9))
            elif kernel in ('andrews', 'quadratic-spectral', 'qs'):
                bw = ceil(20 * (nobs / 100) ** (2 / 25))
            elif kernel in ('parzen', 'gallant'):
                bw = ceil(20 * (nobs / 100) ** (4 / 25))
            else:
                raise ValueError('Unknown kernel {0}'.format(kernel))
        bw = int(bw)
        w = self._kernels[kernel](bw)

        pinvz = self._pinvz
        xhat_e = z @ (pinvz @ x) * eps
        s = xhat_e.T @ xhat_e

        for i in range(bw):
            op = xhat_e[i + 1:].T @ xhat_e[:-(i + 1)]
            s += w[i + 1] * (op + op.T)
        s /= nobs

        return s

    @property
    def config(self):
        return {'debiased': self.debiased,
                'bw': self._bandwidth,
                'kernel': self._kernel,
                'name': self.__class__.__name__}


class OneWayClusteredCovariance(HomoskedasticCovariance):
    r"""
    Covariance estimation for clustered data

    Parameters
    ----------
    x : ndarray
        Model regressors (nobs by nvar)
    y : ndarray
        Series ,modeled (nobs by 1)
    z : ndarray
        Instruments used for endogensou regressors (nobs by ninstr)
    params : ndarray
        Estimated model parameters (nvar by 1)
    debiased : bool, optional
        Flag indicating whether to use a small-sample adjustment
    clusters : ndarray, optional
        Cluster group assignment.  If not provided, uses clusters of 1

    Notes
    -----
    Covariance is estimated using 

    .. math ::

        n^{-1} V^{-1} \hat{S} V^{-1}  

    where 

    .. math:: 

      \hat{S} & = n^{-1} (G/(G-1)) \sum_{g=1}^G \xi_{g}^\prime \xi_{g} \\
      \xi_{g} & = \sum_{i\in\mathcal{G}_g} \hat{\epsilon}_i \hat{x}_i \\ 

    where :math:`\hat{\gamma}=(Z'Z)^{-1}(Z'X)` and 
    :math:`\hat{x}_i = z_i\hat{\gamma}`.  :math:`\mathcal{G}_g` contains the 
    indices of elements in cluster g. If ``debiased`` is true, then 
    :math:`S` is scaled by n / (n-k).

    .. math:: 

      V = n^{-1} X'Z(Z'Z)^{-1}Z'X

    where :math:`X` is the matrix of variables included in the model and 
    :math:`Z` is the matrix of instruments, including exogenous regressors.
    """

    def __init__(self, x, y, z, params, debiased=False, clusters=None):
        super(OneWayClusteredCovariance, self).__init__(x, y, z, params,
                                                        debiased)
        self._clusters = clusters

    @property
    def s(self):
        """One-way clustered estimator of score covariance"""
        x, z, eps = self.x, self.z, self.eps
        pinvz = self._pinvz
        xhat_e = z @ (pinvz @ x) * eps

        nobs, nvar = x.shape
        clusters = self._clusters
        clusters = arange(nobs) if clusters is None else clusters
        self._clusters = clusters
        clusters = clusters.copy().squeeze()
        num_clusters = len(unique(clusters))

        sort_args = argsort(clusters)
        clusters = clusters[sort_args]
        locs = where(r_[True, clusters[:-1] != clusters[1:], True])[0]
        xhat_e = xhat_e[sort_args]

        s = zeros((nvar, nvar))
        for i in range(num_clusters):
            st, en = locs[i], locs[i + 1]
            xhat_e_bar = xhat_e[st:en].sum(axis=0)[:, None]
            s += xhat_e_bar @ xhat_e_bar.T

        s *= num_clusters / (num_clusters - 1) / nobs

        return s

    @property
    def config(self):
        return {'debiased': self.debiased,
                'clusters': self._clusters,
                'name': self.__class__.__name__}
