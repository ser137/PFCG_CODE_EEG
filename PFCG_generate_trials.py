## Generating trials for each participant
    # KEY - input participant code here
    # Using functions and thus parameters defined in utils_trials
    
import os
from pfcg_utils.utils_trials import shuffle_blocks

participant_id = 'Sarah'
######### Set directories## ####################################################
cwd_ = os.getcwd()
datawd = os.path.join(cwd_, 'data')
################################################################################
shuffle_blocks(participant_id, datawd)