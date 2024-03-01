#!/usr/bin/env python
# encoding: utf-8

"""
e108_EventBuilder.py

For this example, original behavioral file had a trial number column, and a
video name column. Each trial has one video, but the video might not be
showing for the entirety of the trial. So what we've done is to use
TrialWise_EventBuilder, which means that we need to implement
events_for_trial() and set trial_field. events_for_trial will be called once
per trial with all of the trial's rows, and we'll look through them to find
the start and stop times for the video, which we'll use to define some events.

You might notice here that we're appending the trial number to the beginning
of the video name. That's because the same video may occur more than once per
run, and we want to be able to differentiate between repetitions as well as
sort the complete list of events by trial number.

"""

import sys
import getopt
from varys.EventBuilder import *
from varys.util import *

class e108_EventBuilder(TrialWise_EventBuilder):
    def __init__(self):
        super(e108_EventBuilder, self).__init__()
        self.subjects = [14]
        self.trial_field = 'TRIAL_INDEX'
        self.data_glob_templates = ['/Volumes/Purkinje/pipe_example/data/%d/txt/*DataViewerResults*.txt']
        self.output_dir = '/Volumes/Purkinje/pipe_example/data/parsed_events/'
    
    def events_for_trial(self, trial_idx, rows):
        # get the trial index
        t_idx = rows[0]['TRIAL_INDEX']
        # find the block of named videos
        first = None
        last = None
        v_name = None
        i_first = None
        for i, row in enumerate(rows):
            vn = row['VIDEO_NAME']
            if v_name == None and len(vn) > 3:
                v_name = vn
                first = row['TIMESTAMP']
                i_first = None
                continue
            if v_name != None and len(vn) <= 3:
                i_last = max(i_first, i-1)
                last = rows[i_last]['TIMESTAMP']
                break
        if last == None and len(rows) > 0:
            last = rows[-1]['TIMESTAMP']
        # make sure we've got the data we need
        if first == None or last == None:
            return []
        # cool - make and return the event
        first = first/1000.
        last = last/1000.
        return [{'name':"%03d_%s" % (t_idx, v_name),
                 'onset':first,
                 'duration':last-first,
                 'set':'vid_events'}]

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
        ax = e108_EventBuilder()
        if subs:
            ax.subjects = subs
        ax.run()
    # catch and report exceptions
    except Exception, err:
        # print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err)
        raise err
        return 2


if __name__ == "__main__":
    sys.exit(main())

