# -*- coding: utf-8 -*-

__author__ = "Austin Hurst"

import os
import random
import klibs
from klibs import P

from klibs.KLConstants import *
from klibs.KLExceptions import TrialException
from klibs.KLTime import CountDown
from klibs.KLBoundary import CircleBoundary
from klibs.KLUtilities import deg_to_px, mouse_pos
from klibs.KLGraphics import NumpySurface, fill, blit, flip
from klibs.KLGraphics import KLDraw as kld
from klibs.KLText import add_text_style
from klibs.KLCommunication import message
from klibs.KLEventQueue import pump
from klibs.KLUserInterface import any_key, ui_request, smart_sleep, key_pressed, hide_cursor
from klibs.KLResponseListeners import KeypressListener
from klibs.KLTrialFactory import TrialIterator

from klibs_wip import block_to_str

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


# TODO:
# - Swap gaze check for saccade check for real Eyelink?


class ExoInstructions(klibs.Experiment):

    def setup(self):

        # Define stimulus sizes
        box_size = deg_to_px(2.3)
        box_thickness = deg_to_px(0.06)
        cue_thickness = deg_to_px(0.24)
        circle_size = deg_to_px(0.82)
        circle_thickness = deg_to_px(0.1)
        target_size = deg_to_px(1.3)
        fixation_size = deg_to_px(0.2)
        add_text_style('target', size='0.6deg', color=WHITE)
        add_text_style('feedback', size='0.7deg', color=WHITE)
        add_text_style('err', size='0.7deg', color=RED)

        # Initialize task stimuli
        self.box = kld.Rectangle(box_size)
        self.box.stroke = [box_thickness, WHITE, STROKE_CENTER]
        self.cue = kld.Rectangle(box_size)
        self.cue.stroke = [cue_thickness, RED, STROKE_CENTER]
        self.circle = kld.Ellipse(circle_size)
        self.circle.stroke = [circle_thickness, WHITE, STROKE_INNER]
        self.fixation = kld.Ellipse(fixation_size, fill=WHITE)
        self.targets = {
            'T': NumpySurface(message("T", style='target')).trim(),
            'F': NumpySurface(message("F", style='target')).trim(),
        }
        self.feedback = {
            0: kld.FixationCross(target_size, cue_thickness, fill=RED, rotation=45),
            1: kld.Ellipse(target_size, fill=GREEN),
        }

        # Stimulus Layout
        locs = {
            'TL': (-1, -1), 'TR': (1, -1), 'BL': (-1, 1), 'BR': (1, 1),
        }
        box_offset = deg_to_px(3.25)
        self.stim_locs = {}
        for name, offsets in locs.items():
            self.stim_locs[name] = (
                P.screen_c[0] + int(box_offset * offsets[0]),
                P.screen_c[1] + int(box_offset * offsets[1])
            )

        # Add fixation boundary to eye tracker
        fix_bounds = CircleBoundary('fixation', P.screen_c, box_size)
        self.el.add_boundary(fix_bounds)

        # Initialize keypress response listener
        self.key_listener = KeypressListener(
            keymap={'T': 'T', 'F': 'F'},
            timeout=2.0,
            loop_callback=self.response_callback,
        )

        # Generate blocks of trials based on custom block structure
        self.blocks, self.block_labels = self.generate_trials()
        self.block_type = None

        self.was_practicing = False
        hide_cursor()
        self.task_demo()
        self.practice_mapping()


    def practice_mapping(self):

        last_loc = 'BL'
        targets = ['T', 'F'] * 10
        random.shuffle(targets)
        for target in targets:
            locs = list(self.stim_locs.keys())
            locs.remove(last_loc)
            target_loc = random.choice(locs)
            last_loc = target_loc
            self.draw_screen(target_loc=target_loc, target=target)
            while True:
                q = pump()
                if key_pressed(target, queue=q):
                    break


    def generate_trials(self):
        # Since this experiment needs a specific sequence of blocks, we load in the
        # trial structure from exp_structure.py here and use it to generate the
        # blocks/trials for the experiment.
        from exp_structure import structure

        block_set = []
        block_labels = []
        block_strs = [] # Text dump of factors for each trial of each block (for debug)

        for block in structure:
            if block.practice and not P.run_practice_blocks:
                continue

            block_labels.append(block.label)
            tmp = block.get_trials()
            if P.max_trials_per_block != None:
                tmp = tmp[:P.max_trials_per_block]

            trials = TrialIterator(tmp)
            trials.practice = block.practice
            block_set.append(trials)

            block_strs.append(block_to_str(block, tmp, len(block_set)))

        # Dump current trial/block structure to a file
        with open(os.path.join(P.local_dir, "trial_dump.txt"), "w") as f:
            f.write("\n".join(block_strs))

        P.blocks_per_experiment = len(block_set)
        return block_set, block_labels


    def block(self):

        # Get block type (accuracy emphasis or RT emphasis)
        self.block_type = self.block_labels[P.block_number - 1]

        # Tell participant when practice block is complete
        if self.was_practicing:
            self.was_practicing = False
            show_demo_text(
                "Practice Complete!\n\nPress any key to begin."
            )

        # If this is the first block for an instruction type, show instructions/demo
        order = ["speed", "accuracy"] if "B" in P.condition else ["accuracy", "speed"]
        txt1 = ("Now that we've explained the task, we'll run through some practice "
                "trials\nto help you get the hang of it.")
        txt2 = ("To get used to the new instructions when responding, you "
                "will now\nperform another block of practice trials.")
        if P.practicing:
            self.was_practicing = True
            if self.block_type == "acc":
                self.show_acc_instructions()
            elif self.block_type == "rt":
                self.show_rt_instructions()
            # Show block start message
            msg = message(txt1 if P.block_number == 1 else txt2, align='center')
            start_msg = message("Press any key to start.")
            fill()
            blit(msg, 8, (P.screen_c[0], P.screen_y * 0.35))
            flip()
            smart_sleep(2000)
            fill()
            blit(msg, 8, (P.screen_c[0], P.screen_y * 0.35))
            blit(start_msg, 5, (P.screen_c[0], P.screen_y * 0.7))
            flip()
            any_key()


    def trial_prep(self):

        # Generate trial factors
        self.cue_onset = random.randrange(1000, 2000, 100)
        if self.cue_validity:
            # If validly-cued target, cue location is target location
            self.cue_loc = self.target_loc
        else:
            # If invalid, choose a random non-target location to cue
            locs = list(self.stim_locs.keys())
            locs.remove(self.target_loc)
            self.cue_loc = random.choice(locs)
        if self.target == 'random':
            # If practice block, randomly choose the target letter
            self.target = random.choice(['T', 'F'])
        self.target_off = False

        # Add timecourse of events to EventManager
        self.evm.add_event('cue_on', self.cue_onset)
        self.evm.add_event('target_on', 300, after='cue_on')
        self.evm.add_event('target_off', 50, after='target_on')

        # Reset trial variables
        self.looked_away = False

        # Perform drift correct before each trial
        self.el.drift_correct(target=self.fixation)


    def trial(self):

        err = "NA"
        edf_markup_suffix = " b{0} t{1}".format(P.block_number, P.trial_number)

        # Draw the initial set of trial stimuli
        self.draw_screen()
        self.el.write("trial_start" + edf_markup_suffix)
        while self.evm.before('cue_on'):
            self.check_fixation()
            self.check_anticipatory()

        # Present the cue
        self.draw_screen(cue_loc=self.cue_loc)
        self.el.write("cue_on" + edf_markup_suffix)
        while self.evm.before('target_on'):
            self.check_fixation()
            self.check_anticipatory()

        # Present the target and collect a response
        self.draw_screen(
            cue_loc=self.cue_loc, target_loc=self.target_loc, target=self.target
        )
        self.el.write("target_on" + edf_markup_suffix)
        resp, rt = self.key_listener.collect()

        # Display feedback after response
        self.el.write("feedback" + edf_markup_suffix)
        if resp:
            accuracy = int(resp == self.target)
            if self.block_type == 'acc':
                feedback = self.feedback[accuracy]
            else:
                style = "feedback"# if accuracy == 1 else "err"
                feedback = message(int(rt), style=style)
            self.show_feedback(feedback, duration=1.0)
        else:
            if self.looked_away:
                feedback = message("Looked away!", style="err")
                err = "looked_away"
            else:
                feedback = message("Too slow!", style="err")
                err = "timeout"
            self.show_feedback(feedback, duration=2.0)
            resp, rt, accuracy = ("NA", "NA", "NA")

        return {
            "block_num": P.block_number,
            "trial_num": P.trial_number,
            "condition": "non-informative" if "NI" in P.condition else "informative",
            "instructions": self.block_type,
            "practice": P.practicing,
            "target": self.target,
            "target_loc": self.target_loc,
            "cue_loc": self.cue_loc,
            "cue_validity": self.cue_validity,
            "rt": rt,
            "response": resp,
            "accuracy": accuracy,
            "err": err,
        }


    def clean_up(self):
        # Show end message so task doesn't just exit abruptly when done
        txt = "You're all done!\n\nPress any key to exit the experiment."
        fill()
        message(txt, location=P.screen_c)
        flip()
        smart_sleep(200)
        any_key()

        # If doing eye tracking, show message when transferring EDF data (can be slow)
        if not "TryLink" in self.el.version:
            fill()
            message("Transferring EyeLink data, please wait...", location=P.screen_c)
            flip()


    def draw_screen(self, cue_loc=None, target_loc=None, target='T'):
        fill()
        blit(self.fixation, 5, P.screen_c)
        for loc in self.stim_locs.keys():
            if cue_loc and loc == cue_loc:
                blit(self.cue, 5, self.stim_locs[loc])
            else:
                blit(self.box, 5, self.stim_locs[loc])
            if target_loc and loc == target_loc:
                blit(self.targets[target], 5, self.stim_locs[loc])
            else:
                blit(self.circle, 5, self.stim_locs[loc])
        flip()


    def show_feedback(self, msg, duration=1.0):
        fill()
        blit(msg, 5, P.screen_c)
        flip()
        feedback_time = CountDown(duration)
        while feedback_time.counting():
            ui_request()


    def check_fixation(self):
        # Recycles the trial if the participant looks away from fixation pre-target
        if not self.el.within_boundary('fixation', EL_GAZE_POS):
            #if self.el.saccade_from_boundary('fixation'):
            self.el.write("recycled (looked away)")
            msg = message("Looked away!", style='err')
            self.show_feedback(msg, duration=2.0)
            raise TrialException("looked away")


    def check_anticipatory(self):
        # Recycles the trial if the participant responds before target appears
        q = pump()
        if key_pressed('T', queue=q) or key_pressed('F', queue=q):
            self.el.write("recycled (anticipatory response)")
            msg = message("Responded too soon!", style='err')
            self.show_feedback(msg, duration=2.0)
            raise TrialException("anticipatory response")


    def response_callback(self):
        # Once it's time, remove the target from the screen
        if not self.target_off and self.evm.after('target_off'):
            self.draw_screen(cue_loc=self.cue_loc)
            self.target_off = True
        # Stop trial and show error if gaze leaves fixation before response
        if not self.el.within_boundary('fixation', EL_GAZE_POS):
            #if self.el.saccade_from_boundary('fixation'):
            self.looked_away = True
            return True


    def task_demo(self):

        fixation = [(self.fixation, P.screen_c)]
        def generate_stimuli(cue_loc=None, target_loc=None, target='T'):
            layout = []
            for loc in self.stim_locs.keys():
                outer = self.cue if (cue_loc and loc == cue_loc) else self.box
                inner = self.circle
                if target_loc and loc == target_loc:
                    inner = self.targets[target]
                layout.append((outer, self.stim_locs[loc]))
                layout.append((inner, self.stim_locs[loc]))
            return layout
        
        show_demo_text(
            "Welcome to the experiment! This tutorial will help explain the task."
        )
        show_demo_text(
            "Each trial of the task begins with 4 squares on the screen.",
            generate_stimuli(),
        )
        show_demo_text(
            "After a brief delay, one of the squares will be highlighted in red.",
            generate_stimuli(cue_loc='TR'),
        )
        show_demo_text(
            ("Shortly after, a letter (T or F) will flash briefly in one of the squares."
             "\nPress any key to see an example."),
            generate_stimuli(cue_loc='TR'),
        )
        show_demo_text(
            [], generate_stimuli(cue_loc='TR') + fixation,
            duration=0.3, wait=False
        )
        show_demo_text(
            [], generate_stimuli(cue_loc='TR', target_loc='TR', target='F') + fixation,
            duration=0.05, wait=False
        )
        show_demo_text(
            [], generate_stimuli(cue_loc='TR') + fixation,
            duration=0.5, wait=False
        )
        show_demo_text(
            ("Your job will be to report the target letter (T or F) by pressing the "
             "\ncorresponding key on the keyboard."),
            generate_stimuli(cue_loc='TR'),
        )
        show_demo_text(
            ("Please note that the target letter can appear in any of the 4 squares,\n"
             "not just the one that was highlighted!"),
            generate_stimuli(cue_loc='TR', target_loc='BL', target='F'),
        )
        show_demo_text(
            ["Before each trial, a dot will appear in the middle of the screen.",
             ("To start a trial, please look directly at the dot and press the "
              "space bar.")],
            fixation, msg_y = int(P.screen_y * 0.32)
        )
        show_demo_text(
            ("During the task, please do your best to keep your eyes fixed on the dot\n"
             "and use your peripheral vision to detect the target letters."),
            fixation, msg_y = int(P.screen_y * 0.35)
        )
        show_demo_text(
            ("The task is self-paced, so feel free to take a break between trials if "
             "you need one!"),
            fixation, msg_y = int(P.screen_y * 0.35)
        )
        show_demo_text(
            ("You will now practice responding to targets by pressing the "
             "corresponding key.\n\nPress any key to begin.")
        )


    def show_acc_instructions(self):
        show_demo_text(
            ("For the next set of trials you will be given feedback on the accuracy of "
             "your responses.\nPlease try to respond as accurately as possible!"),
            [(self.fixation, P.screen_c)], msg_y = int(P.screen_y * 0.35), duration=2.0
        )
        show_demo_text(
            ("When you respond correctly, you will be shown a green circle."),
            [(self.feedback[1], P.screen_c)], msg_y = int(P.screen_y * 0.35)
        )
        show_demo_text(
            ("When you respond *incorrectly*, you will be shown a red X."),
            [(self.feedback[0], P.screen_c)], msg_y = int(P.screen_y * 0.35)
        )


    def show_rt_instructions(self):
        rt_feedback = [(message("374", style="feedback"), P.screen_c)]
        rt_err_feedback = [(message("259", style="err"), P.screen_c)]
        show_demo_text(
            ("For the next set of trials you will be given feedback on the speed of "
             "your responses.\nPlease try to respond as quickly as possible without "
             "guessing!"),
            [(self.fixation, P.screen_c)], msg_y = int(P.screen_y * 0.35), duration=2.0
        )
        show_demo_text(
            ("When you make a response, you will be shown your reaction time (in "
             "milliseconds)."),
            rt_feedback, msg_y = int(P.screen_y * 0.35)
        )
        #show_demo_text(
        #    "If you make an incorrect response, the reaction time will appear in red.",
        #    rt_err_feedback, msg_y = int(P.screen_y * 0.35)
        #)



def show_demo_text(msgs, stim_set=[], duration=1.0, wait=True, msg_y=None):
    """Draws text and stimuli onto the screen for task instructions."""

    msg_x = int(P.screen_x / 2)
    msg_y = int(P.screen_y * 0.5) if msg_y is None else msg_y
    half_space = deg_to_px(0.5)

    # First, render and draw the instruction text to the screen
    fill()
    if not isinstance(msgs, list):
        msgs = [msgs]
    for msg in msgs:
        txt = message(msg, align="center")
        blit(txt, 5, (msg_x, msg_y))
        msg_y += txt.height + half_space

    # Then, draw any example stimuli to the screen
    for stim, locs in stim_set:
        if not isinstance(locs, list):
            locs = [locs]
        for loc in locs:
            blit(stim, 5, loc)
    flip()

    # Keep stimuli on screen for the requested duration, then either continue or
    # wait for a keypress to continue (if wait = True)
    smart_sleep(duration * 1000)
    if wait:
        any_key()
