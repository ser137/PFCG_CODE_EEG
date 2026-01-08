## Stimuli file location defined here, as well as texts displayed throughout the experiment
    # exception - accuracy text is defined in the experiment since it is updated with each block

import os
import ctypes
from psychopy import visual, core, event, monitors, logging, sound
import numpy as np
import importlib.util

# Paths
cwd_    = os.getcwd()
stimwd  = os.path.join(cwd_, 'stimuli')
datawd  = os.path.join(cwd_, 'data')


def preload_stimuli(win, stimuliwd, subjdir):
    # Grating image
    right_grating = [
        visual.ImageStim(win, image=os.path.join(stimuliwd, 'grating_right', f'right_1.png'), 
                        size=None)]

    left_grating = [
        visual.ImageStim(win, image=os.path.join(stimuliwd, 'grating_left', f'left_1.png'), 
                        size=None)]

    # Cues
    cue_baseline = visual.ImageStim(win, image=os.path.join(stimuliwd, 'cue_baseline.png'),
                            size=None)
    cue_cong = visual.ImageStim(win, image=os.path.join(stimuliwd, 'cue_cong.png'),
                            size=None)
    cue_incg = visual.ImageStim(win, image=os.path.join(stimuliwd, 'cue_incg.png'),
                            size=None)
    
    # Fixation Dot
    Fix_Dot = visual.ImageStim(win, image=os.path.join(stimuliwd, 'Fixation_Dot.png'),
                            size=None)
    
    # Text stimuli
    welcome_text = visual.TextStim(win, text='Welcome to the experiment !', color='white', 
                                height=1, pos=(0, 0), units='deg', wrapWidth=60)

    RS_text = visual.TextStim(win, text='We begin by taking a resting state EEG. We ask you to look at following fixation, moving as little as possible, for one minute. When you are ready, press the space bar to begin', color='white', 
                            height=1, pos=(0, 0), units='deg', wrapWidth=60)

    begin_text = visual.TextStim(win, text='The task will now begin. \n\nPlease try to respond as accurately as possible. \n\nPress 8 when you are ready to start.', color='white', 
                                height=1, pos=(0, 0), units='deg', wrapWidth=60)
    # instructions
    instructions_1 = visual.ImageStim(win, image=os.path.join(stimuliwd, f'instructions_1.png'), 
                        size=None)
    instructions_2 = visual.ImageStim(win, image=os.path.join(stimuliwd, f'instructions_2.png'), 
                        size=None)
    
    return {
        "right_grating": right_grating,
        "left_grating": left_grating,
        "cue_baseline": cue_baseline,
        "Fix_Dot": Fix_Dot,
        "cue_cong": cue_cong,
        "cue_incg": cue_incg,
        "welcome_text": welcome_text,
        "RS_text": RS_text,
        "begin_text": begin_text,
        "instructions_1": instructions_1,
        "instructions_2": instructions_2
        }
