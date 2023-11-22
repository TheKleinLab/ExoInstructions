from klibs import P
from klibs.KLStructure import FactorSet
from klibs_wip import Block


# Define the different possible factor sets and session structures

"""
Factors:

- target: The target stimulus for the trial ('T' or 'F').

- target_loc: The location of the target stimulus (top-left, bottom-left,
    top-right, or bottom-right).

- cue_validity: Whether the cue accurately predicts the location of the target.

"""

session_type, order = P.condition.split("-")

if session_type == "NI":
    # If running the non-informative condition, use 25% cue validity
    cue_validity = [True, (False, 3)]
    blocks_per_instruction = 6  # 6 x 32 = 192
else:
    # Otherwise, make the cues 66% informative
    cue_validity = [True, True, False]
    blocks_per_instruction = 8  # 8 x 24 = 192


# Define base set of trial factors

exp_factors = FactorSet({
    'target': ['T', 'F'],
    'target_loc': ['TL', 'TR', 'BL', 'BR'],
    'cue_validity': cue_validity,
})

# Practice blocks are half the length of regular blocks w/ random targets
practice_factors = exp_factors.override({
    'target': ['random']
})


# Define the block types and possible block sequences for the task

acc_practice = Block(practice_factors, label="acc", practice=True)
acc_block = Block(exp_factors, label="acc")

rt_practice = Block(practice_factors, label="rt", practice=True)
rt_block = Block(exp_factors, label="rt")

acc_blocks = [acc_practice] + [acc_block] * blocks_per_instruction
rt_blocks = [rt_practice] + [rt_block] * blocks_per_instruction


# Initialize the experiment structure based on the condition

if order == "A":
    structure = rt_blocks + acc_blocks
else:
    structure = acc_blocks + rt_blocks
