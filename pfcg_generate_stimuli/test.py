## Script to generate single static gratings (90 degrees), fixations and cues
    # Must change monitor specifications here (size, refresh rate etc.), also name of monitor
    # Scaling, visual angle, stimulus parameters
        #  A further visual angle explanation would be great
    # Generates one static grating for left and right (no animation, no phase change)
    # Exporting gratings to grating_left and grating_right folders

## In future: script to generate the cue

import os
import ctypes
from psychopy import visual, core, event, monitors, logging
import numpy as np
from PIL import Image, ImageDraw

# Set current directory
cwd_ = os.getcwd()
mainwd_ = os.path.dirname(cwd_)

#These are the settings for the monitor inside the cabinet 
viewing_distance_cm = 90    
screen_number       = 0
monitor_width_cm    = 53.7
monitor_size_pix    = [1920, 1200]

#Set monitor
monitor = monitors.Monitor("Sudring")
monitor.setWidth(monitor_width_cm)
monitor.setDistance(viewing_distance_cm)
monitor.setSizePix(monitor_size_pix)
monitor.save()

# Grating properties
scaling_factor      = 1  # No scaling
visual_angle_rad    = 5  # Radius of the Gabor patch 
visual_angle_diam   = visual_angle_rad*2  # diameter of the Gabor patch
spatial_freq        = 1.5
orientations        = [180, 180]  # Both gratings have 90 degree orientation
fileid              = ['left', 'right']

# Stimulus parameters
stimulus_size_cm        = 2 * viewing_distance_cm * np.tan(np.deg2rad(visual_angle_diam/2))
pixels_per_cm           = monitor_size_pix[0] / monitor_width_cm
stimulus_diameter_pix   = stimulus_size_cm * pixels_per_cm

win = visual.Window(monitor="Sudring", size=(1920, 1200), screen=0,
                    units="pix", fullscr=False, color=(170,170,170), colorSpace='rgb255')

cue_baseline = visual.Circle(win, radius=visual_angle_rad, fillColor=(90, 90, 90),                   # lineWidth = 10, fillColor=(-1, -1, -1), visual_angle_rad to match the size of the stimuli 
                             lineColor=(90, 90, 90), colorSpace='rgb255', pos=(0, 0), units="deg")
# Draw and save the cues
cue_baseline.draw()
win.flip()
win.getMovieFrame(buffer='front')
core.wait(1)
filename_baseline = 'cue_baselinetest.jpg'
win.saveMovieFrames(os.path.join(mainwd_, 'stimuli', filename_baseline))