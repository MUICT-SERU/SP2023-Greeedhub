#!/usr/bin/env python
# encoding: utf-8

"""
AXCPT_40_EventBuilder.py

Implement an example subclass of RowWise_EventBuilder, and a main function that
will an instantiate an instance of the subclass and run it with the given users
if passed a -s arguement. The -s arguemnt should be a comma separated list of
users to run the script against,
e.g. AXCPT_40_EventBuilder.py -s 1,5,32
"""

import sys
import getopt
from varys.EventBuilder import *
from varys.util import *

class AXCPT_40_EventBuilder(RowWise_EventBuilder):
    is_baseline = None
    def __init__(self):
        super(AXCPT_40_EventBuilder, self).__init__()
        self.subjects = []
        self.data_glob_templates = ['/Volumes/Purkinje/axcpt_pipe_test/data/%d/edat_txt/*.txt']
        self.output_dir = '/Volumes/Purkinje/axcpt_pipe_test/test_output'
    
    def events_for_row(self, row):
        # onset will be in one of these two fields
        onset = row['Probe.OnsetTime'] or row['Probe1.OnsetTime']
        if not onset:
            return []
        onset = onset / 1000. - 1.8
        # acc will be in one of these fields
        acc = row['Probe.ACC'] or row['Probe1.ACC']
        if acc == 1:
            acc = ''
        else:
            acc = '_fail'
        # name will be baseTrial, incentTrial, or nonIncentTrial, with _TrialType appended,
        # with _fail appended to all incorrect trials
        proc = row['Procedure']
        name = None
        if self.is_baseline:
            name = 'baseTrial'
        elif proc == 'rewproc':
            name = 'incentTrial'
        elif proc == 'trialproc':
            name = 'nonIncentTrial'
        if name:
            name += '_' + row['TrialType']
            name += acc
        # okay, if we have everything we need, let's put the events together
        events = []
        if (name and onset):
            events.append({'set':'all_dur0', 'name':name, 'onset':onset, 'duration':0.})
            events.append({'set':'all_dur25', 'name':name, 'onset':onset, 'duration':2.5})
        # return the events
        return events
    
    def handle_run_start(self, run_idx, run_data, file_name):
        self.is_baseline = 'Baseline' in file_name

# The following is provided as an example only... typically, you might simply implement
# the above, and call it from another script.

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
      # parse command line input
        try:
            opts, args = getopt.getopt(argv[1:], 's:')
        except getopt.error, msg:
            raise ValueError('unable to parse input arguments')
        # option processing
        subs = None
        for option, value in opts:
            if option in ('-s'):
                subs = [intify(sub) for sub in value.split(',')]
        # instantiate, configure and run an instance of the subclass
        ax = AXCPT_40_EventBuilder()
        if subs:
            ax.subjects = subs
        ax.run()
    # catch and report exceptions
    except Exception, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err)
        return 2


if __name__ == "__main__":
    sys.exit(main())

