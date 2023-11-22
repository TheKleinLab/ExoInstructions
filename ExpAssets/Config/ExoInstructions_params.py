### Klibs Parameter overrides ###

#########################################
# Runtime Settings
#########################################
collect_demographics = True
manual_demographics_collection = False
manual_trial_generation = True
run_practice_blocks = True
multi_user = False
view_distance = 58 # in centimeters, 57cm = 1 deg of visual angle per cm of screen
allow_hidpi = True

#########################################
# Available Hardware
#########################################
eye_tracker_available = True
eye_tracking = True

#########################################
# Environment Aesthetic Defaults
#########################################
default_fill_color = (32, 32, 32, 255)
default_color = (255, 255, 255, 255)
default_font_size = 0.5
default_font_unit = 'deg'
default_font_name = 'Roboto-Medium'

#########################################
# EyeLink Settings
#########################################
manual_eyelink_setup = False
manual_eyelink_recording = False

saccadic_velocity_threshold = 20
saccadic_acceleration_threshold = 5000
saccadic_motion_threshold = 0.15

#########################################
# Experiment Structure
#########################################
multi_session_project = False
trials_per_block = 0
blocks_per_experiment = 1
max_trials_per_block = None
conditions = ["I-A", "I-B", "NI-A", "NI-B"]
default_condition = "NI-A"

#########################################
# Development Mode Settings
#########################################
dm_auto_threshold = True
dm_trial_show_mouse = False
dm_ignore_local_overrides = False
dm_show_gaze_dot = False

#########################################
# Data Export Settings
#########################################
primary_table = "trials"
unique_identifier = "userhash"
exclude_data_cols = ["created"]
append_info_cols = ["random_seed"]
datafile_ext = ".txt"
append_hostname = False

#########################################
# PROJECT-SPECIFIC VARS
#########################################
