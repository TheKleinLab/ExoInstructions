from klibs import P
from klibs.KLStructure import FactorSet

# Experiment factors defined in ExpAssets/Resources/code/exp_structure.py

exp_factors = FactorSet()

#if P.condition == "NI":
#    # If running the non-informative condition, use 25% cue validity
#    cue_validity = [True, (False, 3)]
#else:
#    # Otherwise, make the cues 66% informative
#    cue_validity = [True, True, False]
#
#exp_factors = FactorSet({
#    'target': ['T', 'F'],
#    'target_loc': ['TL', 'TR', 'BL', 'BR'],
#    'cue_validity': cue_validity,
#})
