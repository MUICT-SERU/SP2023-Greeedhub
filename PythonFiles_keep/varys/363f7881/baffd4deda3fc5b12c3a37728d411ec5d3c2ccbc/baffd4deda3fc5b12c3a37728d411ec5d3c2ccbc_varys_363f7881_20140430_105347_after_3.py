#!/usr/bin/env python
# encoding: utf-8

"""
ETCC_EventBuilder.py

Implement an example subclass of RowWise_EventBuilder, and a main function that
will an instantiate an instance of the subclass and run it with the given users
if passed a -s arguement. The -s arguemnt should be a comma separated list of
users to run the script against,

e.g. ETCC_EventBuilder.py -s 1,5,32

The only things that separate this from AXCPT_40 are that here we implement an
fMRI event set, default to write a fidl file, and subtract a run onset time from
each event onset.
"""

import sys
import getopt
from varys.EventBuilder import *
from varys.util import *

class ETCC_EventBuilder(RowWise_fMRI_EventBuilder):
    is_baseline = None
    is_gravy = None
    run_onset = None
    first_row = False
    run_idx = None
    def __init__(self):
        super(ETCC_EventBuilder, self).__init__()
        self.subjects = [3,5,6]
        self.data_glob_templates = ['/Volumes/Purkinje/fmreyeball/data/s%02d/edats/converted/*.txt']
        self.output_dir = '/Volumes/Purkinje/fmreyeball/data/parsed_events/'
        self.run_field = 'Session'
        self.output_formats = ['fidl']
    
    def events_for_row(self, row):
        # onset will be in one of these two fields
        onset = row['PreCue.OnsetTime'] or row['PreCue1.OnsetTime']
        if not onset:
            return []
        onset = onset / 1000. - self.run_onset
        # acc will be in one of these fields
        acc = row['Probe.ACC'] or row['Probe1.ACC']
        if acc == 1:
            acc = ''
        else:
            acc = '_fail'
        # name will be baseTrial, incentTrial, or nonIncentTrial, with _fail
        # appended to all incorrect trials
        proc = row['Procedure']
        name = None
        if self.is_baseline:
            name = 'baseTrial'
        elif proc == 'rewproc':
            name = 'incentTrial'
        elif proc == 'trialproc':
            name = 'nonIncentTrial'
        if name:
            name += acc
            if self.is_gravy:
                name = 'gravy_' + name
        # we'll use the duration for some event sets
        dur = 12.5 if self.is_gravy else 5.0
        # and we'll use the rt for some
        rt = row['Probe.RT'] or row['Probe1.RT']
        # okay, if we have everything we need, let's put the events together
        events = []
        if (name and onset):
            events.append({'set':'all_dur0', 'name':name, 'onset':onset, 'duration':0., 'rt':rt})
            events.append({'set':'all_dur_real', 'name':name, 'onset':onset, 'duration':dur, 'rt':rt})
            if not acc:
                events.append({'set':'success_dur2_5', 'name':name, 'onset':onset, 'duration':2.5, 'rt':rt})
            if self.is_gravy:
                events.append({'set':'gravy', 'name':name, 'onset':round_to(onset, 2.5), 'duration':17.5})
            if (not self.is_gravy) or acc:
                events.append({'set':'no_gravy', 'name':name, 'onset':round_to(onset, 2.5), 'duration':2.5})
        # last but not least, we want to report the scan start and stop times for every run
        if self.first_row:
            self.first_row = False
            events.append({'set':'gravy', 'name':'scan_start', 'onset':0, 'duration':0})
            events.append({'set':'gravy',
                           'name':'scan_end',
                           'onset':self.duration_for_run(self.run_idx, None, None, None),
                           'duration':0})
        # return the events
        return events
    
    def handle_run_start(self, run_idx, run_data, file_name):
        self.is_baseline = '_BL_' in file_name
        self.is_gravy = '_GR_' in file_name
        self.run_onset = run_data[0]['pause.FinishTime'] / 1000.
        self.first_row = True
        self.run_idx = run_idx

    def tr_count_for_run(self, run_idx, file_name, raw_rows, events):
        """ return the TR count for the given run. """
        if self.is_gravy:
            return 180
        else:
            return 230

    def get_tr(self):
        """ return the TR used for bold runs """
        return 2.5

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
        ax = ETCC_EventBuilder()
        if subs:
            ax.subjects = subs
        ax.run()
    # catch and report exceptions
    except Exception, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err)
        return 2

if __name__ == "__main__":
    sys.exit(main())

