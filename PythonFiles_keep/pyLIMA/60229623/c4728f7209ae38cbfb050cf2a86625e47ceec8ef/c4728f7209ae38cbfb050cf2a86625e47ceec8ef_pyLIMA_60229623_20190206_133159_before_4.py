'''
Welcome to pyLIMA tutorial!

This second example will give you some basics about parameters change.

If you do not like the pyLIMA standard parameters, this is made for you.

We gonna fit the same lightcurves but using different parametrization.
WARNING : this is alpha version, no guarantee
'''


### First import the required libraries

import numpy as np
import matplotlib.pyplot as plt
import os, sys
lib_path = os.path.abspath(os.path.join('../'))
sys.path.append(lib_path)

from pyLIMA import event
from pyLIMA import telescopes
from pyLIMA import microlmodels

### Create an event object. You can choose the name and RA,DEC in degrees :

your_event = event.Event()
your_event.name = 'your choice'
your_event.ra = 269.39166666666665 
your_event.dec = -29.22083333333333

### Now we need some observations. That's good, we obtain some data on two
### telescopes. Both are in I band and magnitude units :

data_1 = np.loadtxt('./Survey_1.dat')
telescope_1 = telescopes.Telescope(name='OGLE', camera_filter='I', light_curve_magnitude=data_1)

data_2 = np.loadtxt('./Followup_1.dat')
telescope_2 = telescopes.Telescope(name='LCOGT', camera_filter='I', light_curve_magnitude=data_2)

### Add the telescopes to your event :
your_event.telescopes.append(telescope_1)
your_event.telescopes.append(telescope_2)

### Find the survey telescope :
your_event.find_survey('OGLE')

### Sanity check
your_event.check_event()


### set gamma for each telescopes :

your_event.telescopes[0].gamma = 0.5
your_event.telescopes[1].gamma = 0.5


### Let's go basic for FSPL :
model_1 = microlmodels.create_model('FSPL', your_event)

### Let's cheat and use the results from example_1 :

model_1.parameters_guess = [79.9, 0.008, 10.1, 0.023]

your_event.fit(model_1,'LM')

### Plot the results

your_event.fits[-1].produce_outputs()
print 'Chi2_LM :',your_event.fits[-1].outputs.fit_parameters.chichi
print 'Fit parameters : ', your_event.fits[-1].fit_results
plt.show()


### All right, look OK. But let's say you dislike the rho parameter. Let's assume you prefer fitting using log(rho). Let's see.

### Start from blind
model_1.parameters_guess = []


### We need to tell pyLIMA what kind of change we want :

model_1.fancy_to_pyLIMA_dictionnary = {'logrho': 'rho'} 
# This means we change rho by log(rho) in the fitting process.

### We need now to explain the mathematical transformation (here we choosed log_10) :

model_1.pyLIMA_to_fancy = {'logrho': lambda parameters: np.log10(parameters.rho) }

### We also need to explain the inverse mathematical transformation :

model_1.fancy_to_pyLIMA = {'rho': lambda parameters: 10 ** parameters.logrho}


### That's it, let's fit!
your_event.fit(model_1,'LM')

your_event.fits[-1].produce_outputs()
print 'Chi2_LM :',your_event.fits[-1].outputs.fit_parameters.chichi
print 'Log rho : ',your_event.fits[-1].outputs.fit_parameters.logrho
print 'Corresponding rho : ',10**your_event.fits[-1].outputs.fit_parameters.logrho

plt.show()

### It works great! 

### OK, you want something more complicated  now : tstar = rho.tE, logrho = log(rho).

### We need to tell pyLIMA what kind of change we want :

model_1.fancy_to_pyLIMA_dictionnary = {'logrho': 'rho', 'tstar':'tE'} 
# This means we change rho by log(rho) and tE by tstar in the fitting process.

### We need now to explain the mathematical transformation :

model_1.pyLIMA_to_fancy = {'logrho': lambda parameters: np.log10(parameters.rho), 
                           'tstar':lambda parameters: parameters.rho*parameters.tE}

### We also need to explain the inverse mathematical transformation :

model_1.fancy_to_pyLIMA = {'rho': lambda parameters: 10 ** parameters.logrho,
                          'tE':lambda parameters: parameters.tstar/10 ** parameters.logrho}


### That's it, let's fit!
your_event.fit(model_1,'LM')

your_event.fits[-1].produce_outputs()
print 'Chi2_LM :',your_event.fits[-1].outputs.fit_parameters.chichi
print 'tstar : ',your_event.fits[-1].outputs.fit_parameters.tstar
print 'Corresponding tE: ',your_event.fits[-1].outputs.fit_parameters.tstar/10**your_event.fits[-1].outputs.fit_parameters.logrho

print 'Log rho : ',your_event.fits[-1].outputs.fit_parameters.logrho
print 'Corresponding rho : ',10**your_event.fits[-1].outputs.fit_parameters.logrho

plt.show()

### And what about the DE method? You need one more step before using these methods with fancy parameters. 
### Take back the precedent example, we need to change the "parameters_boundaries" :

### Change tE boundaries to tstar boundaries (i.e [log10(rhomin)*tEmin, log10(rhomax)*tEmax]) :
model_1.parameters_boundaries[2] = [10**-5, 300 ]

### Change rho boundaries to logrho boundaries (i.e [log10(rhomin), log10(rhomax)]) :
model_1.parameters_boundaries[3] = [-5, -1]


### Let's try it!:
your_event.fit(model_1,'DE')


your_event.fits[-1].produce_outputs()

print 'Chi2_DE :',your_event.fits[-1].outputs.fit_parameters.chichi

print 'tstar : ',your_event.fits[-1].outputs.fit_parameters.tstar

print 'Corresponding tE: ',your_event.fits[-1].outputs.fit_parameters.tstar/10**your_event.fits[-1].outputs.fit_parameters.logrho



print 'Log rho : ',your_event.fits[-1].outputs.fit_parameters.logrho

print 'Corresponding rho : ',10**your_event.fits[-1].outputs.fit_parameters.logrho


plt.show()

# Bonus Track #
### What about some MCMC?

### Let's win some times by injecting some previous results

model_1.parameters_guess = [79.9, 0.008, 0.22849, -1.6459]

### Fit again, but using MCMC now. TAKE A WHILE....Wait until figures pop up.
your_event.fit(model_1,'MCMC',flux_estimation_MCMC='MCMC')
print 'The fitting process is finished now, let produce some outputs....'

your_event.fits[-1].produce_outputs()

plt.show()

