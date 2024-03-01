# -*- coding: utf-8 -*-

from qwt.qt.QtGui import QPolygonF

import numpy as np


class QwtCurveFitter(object):
    def __init__(self):
        pass


class QwtSplineCurveFitter_PrivateData(object):
    def __init__(self):
        self.fitMode = QwtSplineCurveFitter.Auto
        self.splineSize = 250
        self.spline = QwtSpline()


class QwtSplineCurveFitter(QwtCurveFitter):
    
    # enum FitMode
    Auto, Spline, ParametricSpline = range(3)
    
    def __init__(self):
        super(QwtSplineCurveFitter, self).__init__()
        self.d_data = QwtSplineCurveFitter_PrivateData()
    
    def setFitMode(self, mode):
        self.d_data.fitMode = mode
    
    def fitMode(self):
        return self.d_data.fitMode
    
    def setSpline(self, spline):
        self.d_data.spline = spline
        self.d_data.spline.reset()
    
    def spline(self):
        return self.d_data.spline
    
    def setSplineSize(self, splineSize):
        self.d_data.splineSize = max([splineSize, 10])
    
    def splineSize(self):
        return self.d_data.splineSize
    
    def fitCurve(self, points):
        size = points.size()
        if size <= 2:
            return points
        fitMode = self.d_data.fitMode
        if fitMode == self.Auto:
            fitMode = self.Spline
            p = points.data()
            for i in range(1, size):
                if p[i].x() <= p[i-1].x():
                    fitMode = self.ParametricSpline
                    break
        if fitMode == self.ParametricSpline:
            return self.fitParametric(points)
        else:
            return self.fitSpline(points)
    
    def fitSpline(self, points):
        self.d_data.spline.setPoints(points)
        if not self.d_data.spline.isValid():
            return points
        fittedPoints = self.d_data.splineSize
        x1 = points[0].x()
        x2 = points[int(points.size()-1)].x()
        dx = x2 - x1
        delta = dx/(self.d_data.splineSize()-1)
        for i in range(self.d_data.splineSize):
            p = fittedPoints[i]
            v = x1 + i*delta
            sv = self.d_data.spline.value(v)
            p.setX(v)
            p.setY(sv)
        self.d_data.spline.reset()
        return fittedPoints
    
    def fitParametric(self, points):
        size = points.size()
        fittedPoints = QPolygonF(self.d_data.splineSize)
        splinePointsX = QPolygonF(size)
        splinePointsY = QPolygonF(size)
        p = points.data()
        spX = splinePointsX.data()
        spY = splinePointsY.data()
        param = 0.
        for i in range(size):
            x = p[i].x()
            y = p[i].y()
            if i > 0:
                delta = np.sqrt((x-spX[i-1].y())**2+(y-spY[i-1].y())**2)
                param += max([delta, 1.])
            spX[i].setX(param)
            spX[i].setY(x)
            spY[i].setX(param)
            spY[i].setY(y)
        self.d_data.spline.setPoints(splinePointsX)
        if not self.d_data.spline.isValid():
            return points
        deltaX = splinePointsX[size-1].x()/(self.d_data.splineSize-1)
        for i in range(self.d_data.splineSize):
            dtmp = i*deltaX
            fittedPoints[i].setX(self.d_data.spline.value(dtmp))
        self.d_data.spline.setPoints(splinePointsY)
        if not self.d_data.spline.isValid():
            return points
        deltaY = splinePointsY[size-1].x()/(self.d_data.splineSize-1)
        for i in range(self.d_data.splineSize):
            dtmp = i*deltaY
            fittedPoints[i].setY(self.d_data.spline.value(dtmp))
        return fittedPoints


class QwtWeedingCurveFitter_PrivateData(object):
    def __init__(self):
        self.tolerance = 1.
        self.chunkSize = 0

class QwtWeedingCurveFitter_Line(object):
    def __init__(self, i1=0, i2=0):
        self.from_ = i1
        self.to = i2

class QwtWeedingCurveFitter(QwtCurveFitter):
    def __init__(self, tolerance=1.):
        super(QwtWeedingCurveFitter, self).__init__()
        self.d_data = QwtWeedingCurveFitter_PrivateData()
        self.setTolerance(tolerance)
    
    def setTolerance(self, tolerance):
        self.d_data.tolerance = max([tolerance, 0.])
    
    def tolerance(self):
        return self.d_data.tolerance
    
    def setChunkSize(self, numPoints):
        if numPoints > 0:
            numPoints = max([numPoints, 3])
        self.d_data.chunkSize = numPoints
    
    def chunkSize(self):
        return self.d_data.chunkSize
    
    def fitCurve(self, points):
        fittedPoints = QPolygonF()
        if self.d_data.chunkSize == 0:
            fittedPoints = self.simplify(points)
        else:
            for i in range(0, points.size(), self.d_data.chunkSize):
                p = points.mid(i, self.d_data.chunkSize)
                fittedPoints += self.simplify(p)
        return fittedPoints
    
    def simplify(self, points):
        toleranceSqr = self.d_data.tolerance*self.d_data.tolerance
        stack = []
        p = points.data()
        nPoints = points.size()
        usePoint = [False]*nPoints
        stack.insert(0, QwtWeedingCurveFitter_Line(0, nPoints-1))
        raise NotImplementedError
        
    
    
        
    