'''
Created on July 10, 2016
@author: Andrew Abi-Mansour

Center for Materials Sci. & Eng.,
Merck Inc., West Point
'''

# !/usr/bin/python
# -*- coding: utf8 -*- 
# -------------------------------------------------------------------------
#
#   Python module for creating the basic DEM (Granular) object for analysis
#
# --------------------------------------------------------------------------
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -------------------------------------------------------------------------

import numpy as np
import types
from random import choice
from string import ascii_uppercase

class Particles(object):
	""" The Particle class stores all particle properties and the methods that operate on \
these properties """

	def __init__(self, sel = None, **data):

		self.data = data
		self.keys = self.data.keys()

		#for key in self.keys:
		#	if type(self.data[key]) == 'numpy.ndarray':
		#		self.data[key] = self.data[key][sel]

		# Checks if the trajectory file supports reduction in key getters
		# It's important to construct a (lambda) function for each attribute individually
		# so that each dynamically created (property) function would have its own unique
		# key. For instance, placing the for loop below in  _constructAttributes would make
		# all property functions return the same (last) key variable.
		for key in self.keys:
			self._constructAttributes(key)

	def _metaget(self, key):
		"""A meta function for returning dynamic class attributes treated as lists (for easy slicing) 
		and return as numpy arrays for numerical computations / manipulations"""
		
		return self.data[key]

	def _constructAttributes(self, key):
		""" Constructs dynamic functions (getters) for all keys found in the trajectory """

		# We cannot know the information for any property function until that property is created, 
		# so we define the metaget function and particularize it only later with a lambda function			
		method = lambda self: Particles._metaget(self, key)

		setattr(Particles, key, property(fget=method, doc='Extracts {} variable'.format(key)))

	def select(self, sel):
		""" Creates a particle group based on sel string.
		Possible string selections are:

		- bynum 0:N : select particles 0 till N - 1
		- bydist x y z cutoff : select all particles around point (x,y,z) within a distance 'cutoff'
		- byrad radius : select all particles larger

		"""
		sType, sArgs = sel.split()

		if sType == 'bynum':
			s1, s2 = (sArgs.split()[1]).split(':')
			s1, s2 = np.int(s1), np.int(s2)
			sel = np.array(s1,s2)

		if sType == 'byrad':
			radius = np.float(sArgs.split()[1])
			sel = np.find(self.radius >= radius)

		return Particles(sel, **self.data)

	def __getitem__(self, sel):
		return Particles(sel, **self.data)


class Granular(object):
	"""The Granular class contains all the information describing a ganular system.
	A system always requires a trajectory file to read. A trajectory is a (time) 
	series corresponding to the coordinates of all particles in the system. Granular
	handles the time frame and controls i/o operations. It contains a subclass 
	'Paticles' which stores all the particle attributes read from the trajectory file 
	(variables uch as momenta, angular velocities, forces, radii, etc.).
	etc. """

	def __init__(self, fname, const = False):

		self._fname = fname
		self._fp = open(fname, 'r')
		self._length = None # number of lines between two consecutive timesteps
		# this is useful for reading constant N trajectories (i.e. const = True)
		self._const = const

		self.frame = 0
		self.data = {} # a dict that contains either arrays (for storing pos, vels, forces, etc.),
		# scalars (natoms, ) or tuples (box size). ONLY arrays can be slices based on user selection.

		# Do some checking here on the traj extension to make sure
		# it's supported
		self._format = fname.split('.')[-1]

		# Read frame 0 to initialize function getters
		self.__next__()
		self._updateSystem()

	def __iter__(self):
		return self

	def goto(self, frame):
		""" Go to a specific frame in the trajectory. If frame is -1
		then this function will read the last frame """

		# nothing to do
		if frame == self.frame:
			return 0

		# rewind if necessary (better than reading file backwads?)
		if frame < self.frame and frame >= 0:
			self.rewind()

		if self._length:
			self._goto_fast(frame)
		else:
			self._goto_slow(frame)

	def _goto_fast(self, frame):
		""" A fast way of reading a constant N trajectory
		"""
		for i in range((frame - self.frame - 1) * self._length ):
			next(self._fp)

		self.frame += frame - 1

		_goto_slow(frame)

	def _goto_slow(self, frame):
		""" This function assumes self._length is a variable, thus we're reading
		a non-const trajectory. 
		"""

		# find the right frame number
		while self.frame < frame or frame == -1:

			line = self._fp.readline()

			if not line and frame >= 0:
				raise StopIteration('End of file reached.')
			elif not line and frame == -1:
				break

			if line.find('TIMESTEP') >= 0:
				self.frame += 1

		# assert self.frame == frame else something's wrong
		# or the user wants to go to the last frame
		if self.frame == frame:

			timestep = int(self._fp.readline())
			self.data['timestep'] = timestep

			while True:

				line = self._fp.readline()

				if not line and frame >= 0:
					raise StopIteration('End of file reached.')

				if line.find('NUMBER OF ATOMS') >= 0:
					natoms = int(self._fp.readline())
					self.data['natoms'] = natoms

				if line.find('BOX') >= 0:
					boxX = self._fp.readline().split()
					boxY = self._fp.readline().split()
					boxZ = self._fp.readline().split()

					boxX = [float(i) for i in boxX]
					boxY = [float(i) for i in boxY]
					boxZ = [float(i) for i in boxZ]

					self.data['box'] = (boxX, boxY, boxZ)
					break

			line = self._fp.readline()

			if not line and frame >=0:
					raise StopIteration('End of file reached')

			keys = line.split()[2:] # remove ITEM: and ATOMS keywords

			for key in keys:
				self.data[key] = np.zeros(natoms)

			for i in range(natoms):
				var = self._fp.readline().split()

				for j, key in enumerate(keys):
					self.data[key][i] = float(var[j])

			# for convenience, concatenate the x,y,z components
			self._updateSystem()

		else:
			if frame == -1:
				# this is very low and inefficient -- can't we move the file pointer backwards?
				tmp = self.frame
				self.rewind()
				self.goto(tmp)
			else:
				raise NameError('Cannot find frame {} in current trajectory'.format(frame))

		return self.frame

	@property
	def keys(self):
		""" returns the key objects found in the trajctory files """
		return self.data.keys()

	def rewind(self):
		"""Read trajectory from the beginning"""
		self._fp.close()
		self._fp = open(self._fname)
		self.frame = 0
		self.__next__()

	def __next__(self):
		"""Forward one step to next frame when using the next builtin function."""
		return self.next()

	def next(self):
		""" This method updates the system attributes! """
		count = 0

		while True:
			line = self._fp.readline()

			if not line:
				raise StopIteration
			
			if line.find('TIMESTEP') >= 0:
				timestep = int(self._fp.readline())
				self.data['timestep'] = timestep

			if line.find('NUMBER OF ATOMS') >= 0:
				natoms = int(self._fp.readline())
				self.data['natoms'] = natoms

			if line.find('BOX') >= 0:
				boxX = self._fp.readline().split()
				boxY = self._fp.readline().split()
				boxZ = self._fp.readline().split()

				boxX = [float(i) for i in boxX]
				boxY = [float(i) for i in boxY]
				boxZ = [float(i) for i in boxZ]

				self.data['box'] = (boxX, boxY, boxZ)
				break

			count += 1

		line = self._fp.readline()

		if not line:
			raise StopIteration

		self.frame += 1

		keys = line.split()[2:] # remove ITEM: and ATOMS keywords

		for key in keys:
			self.data[key] = np.zeros(natoms)

		for i in range(self.data['natoms']):
			var = self._fp.readline().split()

			for j, key in enumerate(keys):
				self.data[key][i] = float(var[j])

		count += self.data['natoms'] + 1

		self._updateSystem()

		if self._const:
			self._length = count

		return timestep

	def _updateSystem(self):
		""" Makes sure the system is aware of any update in its attributes caused by
		a frame change. """

		self.Particles = Particles(**self.data)
		
	@property
	def granular(self):
		return self

	def __del__(self):
		self._fp.close()

def select(data, *region):	
	"""
	Create a selection of particles based on a subsystem defined by region
	@ region: a tuple (xmin, xmax, ymin, ymax, zmin, zmax). If undefined, all particles are considered.
	"""

	try:
		if not len(region):
			return np.arange(data['NATOMS'], dtype='int')
		else:
			if len(region) != 6:
				print 'Length of region must be 6: (xmin, xmax, ymin, ymax, zmin, zmax)'
				raise

		xmin, xmax, ymin, ymax, zmin, zmax = region

		x, y, z = data['x'], data['y'], data['z']

		# This is so hackish!
		if len(x) > 0:

			indices = np.intersect1d(np.where(x > xmin)[0], np.where(x < xmax)[0])
			indices = np.intersect1d(np.where(y > ymin)[0], indices)
			indices = np.intersect1d(np.where(y < ymax)[0], indices)

			indices = np.intersect1d(np.where(z > zmin)[0], indices)
			indices = np.intersect1d(np.where(z < zmax)[0], indices)

		else:
			indices = []

		return indices

	except:
		raise