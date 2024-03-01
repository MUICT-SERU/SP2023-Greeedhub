#!/usr/bin/env python
# encoding: utf-8

help_message = """

Made for processing edat .txt files from the Negative Motivation study.

parameters
==========
-s (str)
    Comma-separated list of subjects.
-o (str)
    Path where you'd like us to put the parsed files. Will be created if it
    doesn't exist.
-h
    Prints this message.

example
=======
NegMot_EventBuilder.py -s 053_1,053_2 -o ./some_output_directory
"""

import sys
import os
import getopt
from varys.EventBuilder import *
from varys.util import *

REW_PROCS = ["RewardProcText","RewardProcPic"]
NOREW_PROCS = ["NoRewardProcText","NoRewardProcPic"]

class NetMot_EventBuilder(RowWise_fMRI_EventBuilder):
    run_onset = None
    def __init__(self):
        super(NetMot_EventBuilder, self).__init__()
        self.subjects = ["053_1"]
        self.data_glob_templates = ["/data/nil-external/ccp/Negative_Motivation/converted_edats/s%s/*.txt"]
        self.output_dir = "/scratch1/negmot_event_builder/parsed_events/"
        self.run_field = "Procedure[Block]"
        self.output_formats = ["spm","pickle","txt"]
        self.TR = 2.5

    def events_for_row(self, row):
        events = []
        # onset will be in one of these four fields
        onset = (row["Cue3Pic.OnsetTime"] or
                 row["Cue3Text.OnsetTime"] or
                 row["Cue4Pic.OnsetTime"] or
                 row["Cue4.OnsetTime"] or
                 None)
        if onset:
            onset = onset/1000.
            if not self.run_onset:
                self.run_onset = onset - 40.3
            onset = onset - self.run_onset

        # We'll be useing stim type Face/Word as the "name"
        # CueImage - ?/"Face_magenta.tif"/"Face_blue.tif"/"Word_magenta.tif"/"Word_blue.tif"
        # CueType - None / "Attend Face" / "Attend Word"
        cue_stim = row["CueType"] or row["CueImage"] or None
        stim_type = None
        if cue_stim != None:
            stim_type = "Face" if "Face" in cue_stim else "Word"

        if not None in [stim_type, onset]:
            events.append({"set":"cue_onsets",
                           "name":stim_type,
                           "onset":onset,
                           "duration":0})

        # Some commented out stuff you might want to use...
        # # name is based on a few things...
        # targ_rt = row["Target.RT"]
        # targ_acc = row["Target.ACC"]
        # switch_case = row["SwitchRepeat"]
        # trial_proc = row["Procedure[Trial]"]
        # name = None
        # if switch_case == "first":
        #     name = "F"
        # elif targ_rt == 0:
        #     name = "NR"
        # elif targ_acc == 0:
        #     name = "Error"
        # elif switch_case == "switch":
        #     if trial_proc in REW_PROCS:
        #         name = "S_I"
        #     elif trial_proc in NOREW_PROCS:
        #         name = "S_NI"
        # elif switch_case == "repeat":
        #     if trial_proc in REW_PROCS:
        #         name = "R_I"
        #     elif trial_proc in NOREW_PROCS:
        #         name = "R_NI"

        # return the events
        return events
    
    def handle_run_start(self, run_idx, run_data, file_name):
        """ 
        Called at the start of every run. in this case, some subjects will
        have a usable Rest1.OnsetTime, and others will not. So we'll just try
        to use it, and fall back to an alternate method if it fails.
        """
        try:
            self.run_onset = run_data[0]["Rest1.OnsetTime"] / 1000.
        except Exception, e:
            self.run_onset = None

    def tr_count_for_run(self, run_idx, file_name, raw_rows, events):
        """ return the TR count for the given run. """
        return 215

# The following is provided as an example only... typically, you might simply implement
# the above, and call it from another script.

class Usage(Exception):
    def __init__(self, msg=help_message):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
      # parse command line input
        try:
            opts, args = getopt.getopt(argv[1:], 's:o:h')
        except getopt.error, msg:
            raise Usage()
        # option processing
        subs = None
        o_dir = None
        for option, value in opts:
            if option in ('-s'):
                subs = [sub.strip() for sub in value.split(',')]
            if option in ('-o'):
                o_dir = os.path.abspath(value)
                if not os.path.exists(o_dir):
                    os.makedirs(o_dir)
            if option in ('-h'):
                raise Usage()
        # instantiate, configure and run an instance of the subclass
        ax = NetMot_EventBuilder()
        if subs:
            ax.subjects = subs
        if o_dir:
            ax.output_dir = o_dir
        ax.run()
    # catch and report exceptions
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        return 2

if __name__ == "__main__":
    sys.exit(main())

