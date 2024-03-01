'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 27, 2018
@author: Niels Lubbes
'''

from ns_lattice.class_eta import ETA


class TestClassETA():


    def test__update( self ):

        eta = ETA( 10, 2 )
        for i in range( 10 ):
            assert eta.counter == i
            eta.update( '*test*' )
            assert eta.counter == i + 1


if __name__ == '__main__':

    TestClassETA().test__update()
