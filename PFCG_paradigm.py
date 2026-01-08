# Experiment code from scratch (ish)
    # correct_key defined here and in utils_trials. change for EEG
import os
import serial
import csv
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
win = visual.Window(monitor="testMonitor", fullscr=True, # screen=0,              # i think screen_number can be deleted
                    color=("#AAAAAA"), units="deg")


# Hide the mouse !
win.mouseVisible = False
                    
# Set date/time and participant ID
    # Participant ID to match their directory name in the folder 'data'
date_str = datetime.now().strftime("%Y-%m-%d")
participant_id = 'Sarah'
participant_dir = os.path.join(datawd, participant_id)

# import cues and stimuli
    # for modifying relevant stimuli, see utils_stimuli
stimuli = preload_stimuli(win, stimwd, participant_dir)

rt_clock = core.Clock()
rt_clock2 = core.Clock()
onsettime = rt_clock2.getTime()
presenter = StimulusPresenter(window=win, exptimer=rt_clock2, triggers=True)

# Create file path for CSV log
datafile_path = os.path.join(participant_dir, 
                                f"{participant_id}_behaviour_{date_str}.csv")
                                
# Open and write headers if file doesn't exist
if not os.path.exists(datafile_path):
    with open(datafile_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['block', 'trial', 'trialtype', 'trialtype_string', 'cuetype', 'cuetype_string', 'correct_key', 'key_pressed',
                         'is_resp_corr', 'reaction_time'])
        
## Defining Variables                   
symbol_offset = 1.5                     # sets degrees from the centre

## Setting up the experiment
BLOCK = 1               # to be updated with each block. At present, each block is 100 trials, 20 cues 
trialtype = get_block_trialtypes(BLOCK, participant_id, datawd)
cuetype = get_block_cuetypes(BLOCK, participant_id, datawd)
ntrials = len(trialtype)

group_size = 5          # gives trial structure. If changing trial structure, the generation of the trials must also be adjusted in utils_trials
num_groups = ntrials // group_size
    # 8 mini blocks of 5 gratings grouped by congruency as given by the cue

# Initialize accuracy tracking
correct_responses = 0
total_trials = 0

# Iteration for the mini-blocks
for group_idx in range(num_groups):
    
    # Get info each iteration of group
    start_idx = group_idx * group_size
    end_idx = start_idx + group_size

    cueid = cuetype[start_idx]  # Use cuetype from first trial in group
    
    if group_idx == 0:
        stimuli['welcome_text'].draw()
        win.flip()
        keys = event.waitKeys(keyList=["num_5", "escape"])
        if "escape" in keys:
            core.quit()

        stimuli['begin_text'].draw()
        win.flip()
        keys = event.waitKeys(keyList=["num_5", "escape"])
        if "escape" in keys:
            core.quit()
        rt_clock.reset()

        event.clearEvents()

    # Task begins here for each mini-block
    
    # Show baseline cue for 500ms
    stimuli['cue_baseline'].draw()
    win.flip()
    core.wait(0.5)
    
    # Show fixation for 2500ms
    stimuli['Fix_Dot'].draw()
    win.flip()
    core.wait(2.5)

    # Show cue_cong or cue_incg for 500ms
    cue_stimulus = presenter.get_cue_stimulus(stimuli, cueid)
    cue_trigger_code = presenter.get_cue_trigger_code(cueid)
    presenter.present_cue(cue_stimulus, trigger_code=cue_trigger_code)


    # Show fixation. Jitter between 1400-1600ms
    jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
    jitter = round(jitter, 2)
    post_cue_jitter = presenter.present_fixation(stimuli['Fix_Dot'], duration=jitter)

    # Present 5 trials of gratings
    # start_idx and end_idx calling the appropriate row in the data (AKA conditions) file
    for trial_idx in range(start_idx, end_idx):
        trialid = trialtype[trial_idx]
        arrow_stimulus = presenter.target_type(stimuli, trialid)

        # Calculate position within the 5-trial sequence (1-5)
        trial_position = (trial_idx - start_idx) + 1
        target_trigger_code = presenter.get_target_trigger_code(trialid, trial_position)

        event.clearEvents()

        # Generate jitter for fixation duration (1.4-1.6s)
        jitter = np.random.choice(np.arange(1.4, 1.61, 0.01))
        jitter = round(jitter, 2)


        # Send trigger at Flip
        if target_trigger_code is not None:
            win.callOnFlip(presenter.send_trigger, target_trigger_code)
        arrow_stimulus.draw()
        win.flip()

        timer = core.Clock()

        # Initialize response variables
        key_pressed = None
        reaction_time = None
        arrow_duration = 0.5
        response_deadline = arrow_duration + jitter

        # Monitor for responses during target presentation (0.5s)
        while timer.getTime() < arrow_duration:
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
        stimuli['Fix_Dot'].draw()
        win.flip()

        timer = core.Clock()  # Reset timer for fixation period

        # Continue monitoring during fixation if no response yet
        if not key_pressed:
            while timer.getTime() < jitter:
                keys = event.getKeys(keyList=['num_7', 'num_9', 'escape'])
                if keys:
                    key_pressed = keys[0]
                    # RT during fixation = 0.5 + time into fixation
                    reaction_time = arrow_duration + timer.getTime()
                    response_trigger_code = presenter.get_response_trigger_code(key_pressed)
                    presenter.send_trigger(response_trigger_code)
                    if key_pressed == 'escape':
                        core.quit()
                    break
            
            # Wait for any remaining fixation time
            remaining_time = jitter - timer.getTime()
            if remaining_time > 0:
                core.wait(remaining_time)
        else:
            # Response already given during target, just wait the full jitter duration
            core.wait(jitter)

        # Determine trial info for CSV
        correct_key = ''
        trial_num = trial_idx + 1  # or use your CSV's trial column if loaded
        if trialid == 0:
            trialtype_string = 'right_cong'
            correct_key = 'num_9'
        elif trialid == 1:
            trialtype_string = 'left_cong'
            correct_key = 'num_7'
        elif trialid == 2:
            trialtype_string = 'right_incg'
            correct_key = 'num_7'
        elif trialid == 3:
            trialtype_string = 'left_incg'
            correct_key = 'num_9'
        else:
            trialtype_string = 'unknown'
            correct_key = 'unknown'
        cuetype_val = cuetype[trial_idx]
        cuetype_string = 'cong' if cuetype_val == 1 else 'incg'
        block_num = BLOCK

        # Check if the pressed key matches the correct key
        is_resp_corr = []
        if key_pressed == correct_key:
            is_resp_corr = 1
            correct_responses += 1
        else:
            is_resp_corr = 0
        total_trials += 1

        # Write to CSV
        with open(datafile_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                block_num,  # block
                trial_num,  # trial
                trialid,  # trialtype (shows 0,1,2,3)
                trialtype_string,  # trialtype_string (shows left_incg, right_cong, etc.)
                cuetype_val,  # cuetype (shows 0 or 1)
                cuetype_string,  # cuetype_string (shows incg or cong)
                correct_key,  # correct answer
                key_pressed,  # key_pressed
                is_resp_corr,  # correct
                reaction_time,  # reaction time
            ])

# Calculate and display accuracy
if total_trials > 0:
    accuracy_percentage = (correct_responses / total_trials) * 100
else:
    accuracy_percentage = 0

# Create accuracy feedback text
accuracy_text = visual.TextStim(
    win,
    text=f'Block {BLOCK}/10 is now complete. \n\nYou were correct on {accuracy_percentage:.1f}% of trials.\n\nThank you for your participation!',
    color='white',
    height=1,
    pos=(0, 0),
    units='deg',
    wrapWidth=60
)

accuracy_text.draw()
win.flip()
core.wait(10)
