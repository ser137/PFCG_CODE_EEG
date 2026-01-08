import os
from psychopy import visual, core, event, monitors, logging, sound
import psychtoolbox as ptb
import serial
import numpy as np
import csv
import random
import pandas as pd

def get_block_trialtypes(block_number: int, participant_id: str, data_dir: str = "data"):
    csv_path = os.path.join(data_dir, str(participant_id), f"{participant_id}_trials.csv")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Trials CSV not found: {csv_path}")

    trialtypes = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        # Expect headers: block, trial, trialtype
        for row in reader:
            try:
                if int(row["block"]) == block_number:
                    trialtypes.append(int(row["trialtype"]))
            except (KeyError, ValueError) as e:
                raise ValueError(f"Malformed row in {csv_path}: {row}") from e

    return trialtypes

def get_block_cuetypes(block_number: int, participant_id: str, data_dir: str = "data"):
    csv_path = os.path.join(data_dir, str(participant_id), f"{participant_id}_trials.csv")
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Trials CSV not found: {csv_path}")
    cuetypes = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        # Expect headers: block, trial, cuetype
        for row in reader:
            try:
                if int(row["block"]) == block_number:
                    cuetypes.append(int(row["cuetype"]))
            except (KeyError, ValueError) as e:
                raise ValueError(f"Malformed row in {csv_path}: {row}") from e
        
        return cuetypes

"""
RECOMMENDED - keep the following commented out and use the PPTNAME_trials.csv. Gives same trial structure for all participants, while shuffling the block order.
Otherwise, uncomment and run from PFCG_generate_trials.py with participant name/ID.

"""

# def generate_trials_balanced(participant_id, save_dir):
#     """
#     Shuffles the master CSV file randomly, keeping cuetype in groups of 5.
#     Multiple groups of the same cuetype can randomly occur sequentially.
#     Adds a block column, dividing the trials into 10 blocks of 100 trials each.

#     Args:
#         participant_id (str): The participant ID for whom the trials are being generated.
#         save_dir (str): The base directory where the randomized trials will be saved.
#     """
#     # Define paths
#     input_csv_path = os.path.join(save_dir, "master_trials.csv")
#     participant_dir = os.path.join(save_dir, participant_id)
#     output_csv_path = os.path.join(participant_dir, f"{participant_id}_trials.csv")

#     # Ensure the participant-specific folder exists
#     os.makedirs(participant_dir, exist_ok=True)

#     # Load the input CSV file
#     df = pd.read_csv(input_csv_path)

#     # Ensure the input CSV has the required columns
#     required_columns = ['cuetype', 'cuetype_string', 'trialtype', 'trialtype_string', 'correct_key']
#     if not all(col in df.columns for col in required_columns):
#         raise ValueError(f"Input CSV must contain the following columns: {required_columns}")

#     # Shuffle the rows of the dataframe (initial pass)
#     df = df.sample(frac=1, random_state=42).reset_index(drop=True)

#     # Separate the dataframe by cuetype
#     cuetype_0 = df[df['cuetype'] == 0].reset_index(drop=True)
#     cuetype_1 = df[df['cuetype'] == 1].reset_index(drop=True)

#     # Create groups of up to 5 same-cuetype rows (last group for a cuetype may be <5)
#     cuetype_groups = []
#     while len(cuetype_0) >= 5 or len(cuetype_1) >= 5:
#         if len(cuetype_0) >= 5:
#             cuetype_groups.append(cuetype_0.iloc[:5])
#             cuetype_0 = cuetype_0.iloc[5:].reset_index(drop=True)
#         if len(cuetype_1) >= 5:
#             cuetype_groups.append(cuetype_1.iloc[:5])
#             cuetype_1 = cuetype_1.iloc[5:].reset_index(drop=True)

#     # Append any leftover rows (<5) as their own groups so we preserve all trials
#     if len(cuetype_0) > 0:
#         cuetype_groups.append(cuetype_0)
#     if len(cuetype_1) > 0:
#         cuetype_groups.append(cuetype_1)

#     # Helper to compute the maximum run length (consecutive groups of same cuetype)
#     def max_cuetype_run(groups_order):
#         max_run = 0
#         cur_run = 0
#         last_type = None
#         for g in groups_order:
#             t = int(g['cuetype'].iloc[0])
#             if t == last_type:
#                 cur_run += 1
#             else:
#                 cur_run = 1
#                 last_type = t
#             if cur_run > max_run:
#                 max_run = cur_run
#         return max_run

#     # Try randomized shuffles to find an ordering with <= 3 consecutive same-cuetype groups
#     attempts = 5000
#     found_order = None
#     for _ in range(attempts):
#         random.shuffle(cuetype_groups)
#         if max_cuetype_run(cuetype_groups) <= 4:
#             found_order = list(cuetype_groups)
#             break

#     # If random tries fail, use a greedy arranger that alternates groups while preventing runs > 4
#     if found_order is None:
#         groups0 = [g for g in cuetype_groups if int(g['cuetype'].iloc[0]) == 0]
#         groups1 = [g for g in cuetype_groups if int(g['cuetype'].iloc[0]) == 1]
#         random.shuffle(groups0)
#         random.shuffle(groups1)

#         arranged = []
#         last_type = None
#         run = 0
#         while groups0 or groups1:
#             choose_from = None
#             if run == 4:
#                 # must switch if possible
#                 if last_type == 0 and groups1:
#                     choose_from = 1
#                 elif last_type == 1 and groups0:
#                     choose_from = 0
#             if choose_from is None:
#                 # prefer the side with more remaining groups
#                 if len(groups0) > len(groups1):
#                     choose_from = 0
#                 elif len(groups1) > len(groups0):
#                     choose_from = 1
#                 else:
#                     choose_from = 0 if random.random() < 0.5 else 1

#             if choose_from == 0 and groups0:
#                 g = groups0.pop()
#                 t = 0
#             elif choose_from == 1 and groups1:
#                 g = groups1.pop()
#                 t = 1
#             else:
#                 # fallback: take whatever is available
#                 if groups0:
#                     g = groups0.pop(); t = 0
#                 else:
#                     g = groups1.pop(); t = 1

#             arranged.append(g)
#             if last_type == t:
#                 run += 1
#             else:
#                 last_type = t
#                 run = 1

#         found_order = arranged

#     # Final sanity check and warning if constraint not met
#     if max_cuetype_run(found_order) > 4:
#         logging.warning("Unable to fully enforce <=4 consecutive cuetype groups; produced ordering has max run %d", max_cuetype_run(found_order))

#     # Combine ordered groups back into a dataframe (preserving internal order)
#     randomized_df = pd.concat(found_order).reset_index(drop=True)

#     # Add the block column (same as before)
#     randomized_df['block'] = (randomized_df.index // 100) + 1

#     # Save
#     randomized_df.to_csv(output_csv_path, index=False)
#     print(f"Randomized trials successfully written to: {output_csv_path}")

#def generate_practice_trials(participant_id, save_dir):
#    """
#    Creates a practice block with 50 trials from master_trials.csv.
#    Maintains the same cuetype grouping constraints (groups of 5, max 4 consecutive same-cuetype groups).
#    
#    Args:
#        participant_id (str): The participant ID for whom the practice trials are being generated.
#        save_dir (str): The base directory where the practice trials will be saved.
#    """
#    # Define paths
#    input_csv_path = os.path.join(save_dir, "master_trials.csv")
#    participant_dir = os.path.join(save_dir, participant_id)
#    output_csv_path = os.path.join(participant_dir, f"{participant_id}_trials.csv")
#
#    # Ensure the participant-specific folder exists
#    os.makedirs(participant_dir, exist_ok=True)
#
#    # Load the input CSV file
#    df = pd.read_csv(input_csv_path)
#
#    # Ensure the input CSV has the required columns
#    required_columns = ['cuetype', 'cuetype_string', 'trialtype', 'trialtype_string', 'correct_key']
#    if not all(col in df.columns for col in required_columns):
#        raise ValueError(f"Input CSV must contain the following columns: {required_columns}")
#
#    # Randomly sample 50 rows from master_trials.csv
#    df_practice = df.sample(n=50, random_state=None).reset_index(drop=True)
#
#    # Separate by cuetype
#    cuetype_0 = df_practice[df_practice['cuetype'] == 0].reset_index(drop=True)
#    cuetype_1 = df_practice[df_practice['cuetype'] == 1].reset_index(drop=True)
#
#    # Create groups of up to 5 same-cuetype rows
#    cuetype_groups = []
#    while len(cuetype_0) >= 5 or len(cuetype_1) >= 5:
#        if len(cuetype_0) >= 5:
#            cuetype_groups.append(cuetype_0.iloc[:5])
#            cuetype_0 = cuetype_0.iloc[5:].reset_index(drop=True)
#        if len(cuetype_1) >= 5:
#            cuetype_groups.append(cuetype_1.iloc[:5])
#            cuetype_1 = cuetype_1.iloc[5:].reset_index(drop=True)
#
#    # Append any leftover rows (<5) as their own groups
#    if len(cuetype_0) > 0:
#        cuetype_groups.append(cuetype_0)
#    if len(cuetype_1) > 0:
#        cuetype_groups.append(cuetype_1)
#
#    # Helper to compute the maximum run length
#    def max_cuetype_run(groups_order):
#        max_run = 0
#        cur_run = 0
#        last_type = None
#        for g in groups_order:
#            t = int(g['cuetype'].iloc[0])
#            if t == last_type:
#                cur_run += 1
#            else:
#                cur_run = 1
#                last_type = t
#            if cur_run > max_run:
#                max_run = cur_run
#        return max_run
#
#    # Try randomized shuffles to find an ordering with <= 4 consecutive same-cuetype groups
#    attempts = 5000
#    found_order = None
#    for _ in range(attempts):
#        random.shuffle(cuetype_groups)
#        if max_cuetype_run(cuetype_groups) <= 4:
#            found_order = list(cuetype_groups)
#            break
#
#    # If random tries fail, use greedy arranger
#    if found_order is None:
#        groups0 = [g for g in cuetype_groups if int(g['cuetype'].iloc[0]) == 0]
#        groups1 = [g for g in cuetype_groups if int(g['cuetype'].iloc[0]) == 1]
#        random.shuffle(groups0)
#        random.shuffle(groups1)
#
#        arranged = []
#        last_type = None
#        run = 0
#        while groups0 or groups1:
#            choose_from = None
#            if run == 4:
#                if last_type == 0 and groups1:
#                    choose_from = 1
#                elif last_type == 1 and groups0:
#                    choose_from = 0
#            if choose_from is None:
#                if len(groups0) > len(groups1):
#                    choose_from = 0
#                elif len(groups1) > len(groups0):
#                    choose_from = 1
#                else:
#                    choose_from = 0 if random.random() < 0.5 else 1
#
#            if choose_from == 0 and groups0:
#                g = groups0.pop()
#                t = 0
#            elif choose_from == 1 and groups1:
#                g = groups1.pop()
#                t = 1
#            else:
#                if groups0:
#                    g = groups0.pop(); t = 0
#                else:
#                    g = groups1.pop(); t = 1
#
#            arranged.append(g)
#            if last_type == t:
#                run += 1
#            else:
#                last_type = t
#                run = 1
#
#        found_order = arranged
#
#    # Combine ordered groups back into a dataframe
#    practice_df = pd.concat(found_order).reset_index(drop=True)
#
#    # Add block column (all practice trials are block 7)
#    practice_df['block'] = 'PRACT'
#
#    # Save
#    practice_df.to_csv(output_csv_path, index=False)
#    print(f"Practice trials successfully written to: {output_csv_path}")

def shuffle_blocks(participant_id, save_dir):
    """
    Shuffles the blocks from the master_blocks.csv file
    Saves to the participant directory
    """
    # Define paths
    input_csv_path = os.path.join(save_dir, "master_blocks.csv")
    participant_dir = os.path.join(save_dir, participant_id)
    output_csv_path = os.path.join(participant_dir, f"{participant_id}_trials.csv")
    
    # Load the input CSV file
    df = pd.read_csv(input_csv_path)
    
    # Get unique block numbers
    unique_blocks = df['block'].unique()
    
    # Shuffle the block order
    shuffled_blocks = np.random.permutation(unique_blocks)
    
    # Create a mapping from old block numbers to new block numbers
    block_mapping = {old_block: new_block for new_block, old_block in enumerate(shuffled_blocks, start=1)}
    
    # Reorder dataframe by shuffled blocks
    df_shuffled = pd.concat([df[df['block'] == block] for block in shuffled_blocks]).reset_index(drop=True)
    
    # Update block numbers to sequential ordering (1, 2, 3, ...)
    df_shuffled['block'] = df_shuffled['block'].map(block_mapping)
    
    # Save to participant-specific file
    df_shuffled.to_csv(output_csv_path, index=False)
    print(f"Shuffled blocks successfully written to: {output_csv_path}")
    
    
