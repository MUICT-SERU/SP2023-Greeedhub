# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 20:43:25 2015

@author: mercierthomas
"""
import numpy                     # we import the array library
from matplotlib import pyplot    # import plotting library
import scipy.io                  # input/output library
import scipy.stats               # statistics library
import statsmodels.api as sm     # for time series analysis and regressions
from statsmodels.graphics.api import qqplot
from scipy.fftpack import fft    # fast fourier transform
from datetime import timedelta
from datetime import datetime
import pandas
# import xlrd                      # to read .xls files
# from arch import arch_model
import csv
import pytz

def generate(n,length,Start_date):
    # The module will generate n scenarios of frequency deviations    
    # The frequency-deviations series will be composed of a number length of time steps
    # Start_date is a vector indicating the date at which the time series should begin
    # Start_date = [2015,1,1,0] will make the time series start on 1 January 2015 at 00:00 am
    
    
    mean = 50.00021868201017
    Means3 = numpy.zeros((12,2,24,4))
    for i in range(11):
        for j in range(2):
            ifile  = open('/Users/mercierthomas/Desktop/RTE_Frequency_analysis/Mat_' + str(i+1) + '_' + str(j+1) + '_X_X.csv', "rb")
            reader = csv.reader(ifile, delimiter = ';')
            rownum = 0
            for row in reader:
                colnum = 0
                for col in row:
                    Means3[i,j,rownum,colnum] = float(col)
                    colnum += 1
                rownum += 1
            ifile.close()
        
    
    tz = pytz.timezone('Europe/Brussels')
    Date_Time = tz.normalize(datetime(Start_date[0], Start_date[1], Start_date[2], Start_date[3], 0, tzinfo=pytz.utc))
    Months = numpy.zeros(length)
    Weekdays = numpy.zeros(length)
    Hours = numpy.zeros(length)
    Quarters = numpy.zeros(length)
    delta = timedelta(minutes=15)
    for i in range(length): 
        Hours[i] = Date_Time.hour
        Quarters[i] = Date_Time.minute/15
        Months[i] = Date_Time.month - 1
        Weekdays[i] = 1*(Date_Time.weekday() >= 5)
        Date_Time = tz.normalize(Date_Time + delta)
    
    
    m = -0.0001397577
    sd = 0.0094688303
    nu = 4.0000006036 
    
    x = numpy.linspace(-0.35,0.35,100)
    stud_cdf = scipy.stats.t.cdf(numpy.linspace(-0.35,0.35,100), nu, m, numpy.sqrt(sd))
    #pyplot.plot(x,stud_cdf)
    
    phi1 = 4.234e-01
    phi2 = 6.860e-02
    phi3 = 7.631e-02
    phi4 = 1.392e-01
    alpha = 7.183e-01
    beta = 9.716e-02
    sigma = 1.708e-05
    
    epsilon = numpy.zeros(2)
    sigma_t = numpy.zeros(2)
    Freq = numpy.zeros((length,n))
    
    for k in range(n):
        epsilon_x = numpy.random.rand()
        i = 0
        while epsilon_x > stud_cdf[i] and i < 98:
            i = i + 1
        epsilon[1] = x[i]
        
        
        epsilon_x = numpy.random.rand()
        i = 0
        while epsilon_x > stud_cdf[i] and i < 98:
            i = i + 1
        epsilon[0] = epsilon[1]
        epsilon[1] = x[i]
        sigma_t[0] = sigma_t[1]
        sigma_t[1] = numpy.sqrt(sigma + beta*sigma_t[0]*sigma_t[0] + alpha*epsilon[0]*epsilon[0])
        Freq[1,k] = phi1*Freq[0,k] + sigma_t[1]*epsilon[1]
        
        
        epsilon_x = numpy.random.rand()
        i = 0
        while epsilon_x > stud_cdf[i] and i < 98:
            i = i + 1
        
        epsilon[0] = epsilon[1]
        epsilon[1] = x[i]
        sigma_t[0] = sigma_t[1]
        sigma_t[1] = numpy.sqrt(sigma + beta*sigma_t[0]*sigma_t[0] + alpha*epsilon[0]*epsilon[0])
        Freq[2,k] = phi1*Freq[1,k] + phi2*Freq[0,k] + sigma_t[1]*epsilon[1]
        
        epsilon_x = numpy.random.rand()
        i = 0
        while epsilon_x > stud_cdf[i] and i < 98:
            i = i + 1
        epsilon[0] = epsilon[1]
        epsilon[1] = x[i]
        sigma_t[0] = sigma_t[1]
        sigma_t[1] = numpy.sqrt(sigma + beta*sigma_t[0]*sigma_t[0] + alpha*epsilon[0]*epsilon[0])
        Freq[3,k] = phi1*Freq[2,k] + phi2*Freq[1,k] + phi3*Freq[0,k] + sigma_t[1]*epsilon[1]
        
        
        for i in range(length):
            if i >= 4:
                epsilon_x = numpy.random.rand()
                j = 0
                while epsilon_x > stud_cdf[j] and j < 98:
                    j = j + 1
                epsilon[0] = epsilon[1]
                epsilon[1] = x[j]
                sigma_t[0] = sigma_t[1]
                sigma_t[1] = numpy.sqrt(sigma + beta*sigma_t[0]*sigma_t[0] + alpha*epsilon[0]*epsilon[0])
                Freq[i,k] = phi1*Freq[i-1,k] + phi2*Freq[i-2,k] + phi3*Freq[i-3,k] + phi4*Freq[i-4,k] + sigma_t[1]*epsilon[1]
        
        for i in range(length):
            Freq[i,k] = Freq[i,k] + mean + Means3[Months[i], Weekdays[i], Hours[i], Quarters[i]]
    
    return Freq