# Practice version of PFCG paradigm - no CSV output
import os
import serial
import numpy as np
from datetime import datetime
from psychopy import logging, prefs, core, visual, event, monitors
from PFCG_cfg import stimwd, datawd, preload_stimuli
from pfcg_utils.utils_stimuli import StimulusPresenter, sec_to_fr
from pfcg_utils.utils_trials import get_block_trialtypes, get_block_cuetypes
import random


# Change the size depending on the monitor in question, also monitor name
viewing_distance_cm = 90    
screen_number       = 1
monitor_width_cm    = 53.7
monitor_size_pix    = [1920, 1200]

#Set monitor
monitor = monitors.Monitor("Sudring")
monitor.setWidth(monitor_width_cm)
monitor.setDistance(viewing_distance_cm)
monitor.setSizePix(monitor_size_pix)
monitor.save()

# Create the window with aforementioned monitor
win = visual.Window(monitor="testMonitor", fullscr=True,
                    color=("#AAAAAA"), units="deg")


# Hide the mouse !
win.mouseVisible = False
                    
# Set participant ID for loading stimuli
participant_id = 'Practice'
participant_dir = os.path.join(datawd, participant_id)

# import cues and stimuli
stimuli = preload_stimuli(win, stimwd, participant_dir)

rt_clock = core.Clock()
rt_clock2 = core.Clock()
onsettime = rt_clock2.getTime()
presenter = StimulusPresenter(window=win, exptimer=rt_clock2, triggers=True)

#  CHECK IN EEG LAB - are these different clocks needed?
# rt_clock = core.Clock()
# rt_clock2 = core.Clock()
# onsettime = rt_clock2.getTime()
# presenter = StimulusPresenter(window=win, exptimer=rt_clock2, triggers=True)

## Defining Variables                   
symbol_offset = 1.5

## Setting up the practice
BLOCK = 0               
trialtype = get_block_trialtypes(BLOCK, participant_id, datawd)
cuetype = get_block_cuetypes(BLOCK, participant_id, datawd)
ntrials = len(trialtype)

group_size = 5
num_groups = ntrials // group_size

# Initialize accuracy tracking
correct_responses = 0
total_trials = 0

# Iteration for the mini-blocks
for group_idx in range(num_groups):
    
    # Get info each iteration of group
    start_idx = group_idx * group_size
    end_idx = start_idx + group_size

    cueid = cuetype[start_idx]
    
    if group_idx == 0:
        # Practice instructions
        stimuli['instructions_1'].draw()
        win.flip()
        keys = event.waitKeys(keyList=["num_5", "escape"])
        if "escape" in keys:
            core.quit()
        rt_clock.reset()

        event.clearEvents()
        
        stimuli['instructions_2'].draw()
        win.flip()
        keys = event.waitKeys(keyList=["num_5", "escape"])
        if "escape" in keys:
            core.quit()
        rt_clock.reset()

        event.clearEvents()

        stimuli['begin_text'].draw()
        win.flip()
        keys = event.waitKeys(keyList=["num_5", "escape"])
        if "escape" in keys:
            core.quit()
        rt_clock.reset()

        event.clearEvents()

    # Task begins here for each mini-block

    # Show cue
    cue_stimulus = presenter.get_cue_stimulus(stimuli, cueid)
    cue_trigger_code = presenter.get_cue_trigger_code(cueid)
    presenter.present_cue(cue_stimulus, trigger_code=cue_trigger_code)

    # Show fixation with jitter
    jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
    jitter = round(jitter, 2)
    post_cue_jitter = presenter.present_fixation(stimuli['Fixation_Square'], duration=jitter)

    # Present 5 trials
    for trial_idx in range(start_idx, end_idx):
        trialid = trialtype[trial_idx]
        square_stimulus = presenter.target_type(stimuli, trialid)

        trial_position = (trial_idx - start_idx) + 1
        target_trigger_code = presenter.get_target_trigger_code(trialid, trial_position)

        event.clearEvents()

        # Generate jitter
        jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
        jitter = round(jitter, 2)

        # Send trigger at Flip
        if target_trigger_code is not None:
            win.callOnFlip(presenter.send_trigger, target_trigger_code)
        square_stimulus.draw()
        win.flip()

        timer = core.Clock()

        # Initialize response variables
        key_pressed = None
        reaction_time = None
        square_duration = 0.5
        response_deadline = square_duration + jitter

        # Monitor for responses during target presentation
        while timer.getTime() < square_duration:
            keys = event.getKeys(keyList=['num_7', 'num_9', 'escape'])
            if keys:
                key_pressed = keys[0]
                reaction_time = timer.getTime()
                response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                presenter.send_trigger(response_trigger_code)
                if key_pressed == 'escape':
                    core.quit()
                break

        # Show fixation
        win.callOnFlip(presenter.send_trigger, 9)
        stimuli['Fixation_Square'].draw()
        win.flip()

        timer = core.Clock()

        # Continue monitoring during fixation if no response yet
        if not key_pressed:
            while timer.getTime() < response_deadline:
                keys = event.getKeys(keyList=['num_7', 'num_9', 'escape'])
                if keys:
                    key_pressed = keys[0]
                    reaction_time = timer.getTime()
                    response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                    presenter.send_trigger(response_trigger_code)
                    if key_pressed == 'escape':
                        core.quit()
                    break

        # Wait for remaining fixation time
        remaining_time = response_deadline - timer.getTime()
        if remaining_time > 0:
            core.wait(remaining_time)

        # Determine correct key for accuracy tracking
        correct_key = ''
        if trialid == 0:
            correct_key = 'num_9'
        elif trialid == 1:
            correct_key = 'num_7'
        elif trialid == 2:
            correct_key = 'num_7'
        elif trialid == 3:
            correct_key = 'num_9'

        # Track accuracy
        if key_pressed == correct_key:
            correct_responses += 1
        total_trials += 1

# Calculate and display accuracy
if total_trials > 0:
    accuracy_percentage = (correct_responses / total_trials) * 100
else:
    accuracy_percentage = 0

# Create accuracy feedback text
accuracy_text = visual.TextStim(
    win,
    text=f'Practice complete!\n\nYou were correct on {accuracy_percentage:.1f}% of trials.\n\nPress SPACE to continue.',
    color='white',
    height=1,
    pos=(0, 0),
    units='deg',
    wrapWidth=60
)

accuracy_text.draw()
win.flip()
core.wait(10)
win.close()
core.quit()