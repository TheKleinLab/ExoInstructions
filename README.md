# ExoInstructions

ExoInstructions is a paradigm for studying how task instructions affect the speed and accuracy of responses in an exogenous spatial cueing task.

![ExoInstructions](task.gif)

The stimuli and general design of the task are based on Experiments 1-4 in [Prinzmetal, McCool, and Park (2005)](https://doi.org/10.1037/0096-3445.134.1.73). During the task, 4 placeholder boxes are shown on screen at equal distances from a fixation point. After a brief semi-random delay, a cue appears highlighting one of the 4 boxes in red. 300 ms after the cue appears, a target (the letter T or F) very briefly replaces the circle in the middle of one of the box locations (not necessarily the one that was cued). Once the target appears, the task of the participant is to identify the target letter by pressing the corresponding key on the keyboard.

To manipulate the speed-accuracy bias within participants, the task is split into two halves: one where participants are instructed to respond *as quickly as possible without guessing* (RT instructions), and one where the participants are instructed to respond *as accurately as possible* (accuracy instructions). During RT instruction blocks, participants are shown their reaction time as feedback following each response (as illustrated above). During accuracy instruction blocks, participants are instead shown either a green circle (if they responded correctly) or a red X (if they responded incorrectly) as feedback. 

## Requirements

ExoInstructions is programmed in Python 3.9 using the [KLibs framework](https://github.com/a-hurst/klibs). It has been developed and tested on recent versions of macOS and Linux, but should also work without issue on Windows systems.

The task also requires an SR Research EyeLink eye tracker, but can be run and tested without one using a fallback mouse simulation mode.


## Getting Started

### Installation

First, you will need to install the KLibs framework by following the instructions [here](https://github.com/a-hurst/klibs).

Then, you can then download and install the experiment program with the following commands (replacing `~/Downloads` with the path to the folder where you would like to put the program folder):

```
cd ~/Downloads
git clone https://github.com/TheKleinLab/ExoInstructions.git
```

To run the task with a hardware eye tracker, you will also need to have the [EyeLink Developer's Kit](https://www.sr-research.com/support/thread-13.html) installed on your system (requires registering for a free account on the SR Support forums).

To install all Python dependencies for the task in a self-contained environment with Pipenv, run `pipenv install` while in the ExoInstructions folder (Pipenv must be already installed).

### Running the Experiment

ExoInstructions is a KLibs experiment, meaning that it is run using the `klibs` command at the terminal (running the 'experiment.py' file using Python directly will not work).

To run the experiment, navigate to the ExoInstructions folder in Terminal and run `klibs run [screensize]`, replacing `[screensize]` with the diagonal size of your display in inches (e.g. `klibs run 21.5` for a 21.5-inch monitor). Note that the stimulus sizes for the study assume that a) the screen size for the monitor has been specified accurately, and b) that participants are seated approximately 57 cm from the screen (the exact view distance can be modified in the project's `params.py` file).

If running the task in a self-contained Pipenv environment, simply prefix all `klibs` commands with `pipenv run` (e.g. `pipenv run klibs run 21.5`).

If you just want to test the program out for yourself and skip demographics collection, you can add the `-d` flag to the end of the command to launch the experiment in development mode.

#### Optional Settings

There are two variations of the task that can be run: one where cues are 66% informative of the target location (I), and one where cues are completely uninformative (NI). Each of these variations has two possible instruction orders: RT -> accuracy (A), or accuracy -> RT (B), resulting in four possible between-subjects conditions:

Condition Code | Cue Validity | Instruction Order
--- | --- | ---
`NI-A` | 25% Valid | RT first
`NI-B` | 25% Valid | Accuracy first
`I-A` | 66% Valid | RT first
`I-B` | 66% Valid | Accuracy first

To choose which condition to run, launch the experiment with the `--condition` or `-c` flag, followed by either `NI-A`, `NI-B`, `I-A` or `I-B`. For example, if you wanted to run a participant in the informative cue group with an accuracy-first order condition on a computer with a 24-inch monitor, you would run

```
klibs run 24 --condition I-B
```

If no condition is manually specified, the experiment program will default to non-informative cues with an RT-first order (NI-A).
 

### Exporting Data

To export data from the task, simply run

```
klibs export
```

while in the root of the ExoInstructions directory. This will export the trial data for each participant into individual tab-separated text files in the project's `ExpAssets/Data` subfolder.

The raw EyeLink data files (EDFs) recorded during the task are automatically copied over into the `ExpAssets/EDF` folder each time the experiment exits successfully.